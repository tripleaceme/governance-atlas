// GET /api/download?ref=<paystack reference>            -> what the payment bought
// GET /api/download?ref=<reference>&file=<filename>      -> the file itself
//
// Every request re-verifies the reference with Paystack before releasing
// anything. Nothing is trusted from the client except the reference, and a
// reference only unlocks the files belonging to the item it paid for.
//
// Required environment:
//   PAYSTACK_SECRET_KEY   secret
//   TEMPLATES             R2 bucket binding holding the built documents
//
// The documents live in R2 rather than in the site output because everything in
// a Pages build is publicly fetchable — a paid file served from /templates/
// would simply be a free file with an extra step.

import { CATALOGUE, json } from "../_lib/catalogue.js";

const MIME = {
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  pdf: "application/pdf",
  zip: "application/zip",
};

async function verify(reference, env) {
  const res = await fetch(
    `https://api.paystack.co/transaction/verify/${encodeURIComponent(reference)}`,
    { headers: { Authorization: `Bearer ${env.PAYSTACK_SECRET_KEY}` } },
  );
  const payload = await res.json().catch(() => ({}));
  if (!res.ok || !payload.status) return { ok: false, error: "Could not verify the payment." };

  const d = payload.data || {};
  if (d.status !== "success") return { ok: false, error: `Payment ${d.status || "not completed"}.` };

  const key = d.metadata && d.metadata.item;
  const item = CATALOGUE[key];
  if (!item) return { ok: false, error: "This payment is not linked to a template." };

  // Guard against a transaction created elsewhere for a smaller amount.
  if (typeof d.amount === "number" && d.amount < item.price) {
    return { ok: false, error: "The amount paid does not match this template." };
  }

  return { ok: true, key, item, email: d.customer && d.customer.email };
}

export async function onRequestGet({ request, env }) {
  if (!env.PAYSTACK_SECRET_KEY || !env.TEMPLATES) {
    return json({ error: "Downloads are not configured yet." }, 503);
  }

  const url = new URL(request.url);
  const reference = url.searchParams.get("ref");
  const file = url.searchParams.get("file");

  if (!reference) return json({ error: "Missing payment reference." }, 400);

  const check = await verify(reference, env);
  if (!check.ok) return json({ error: check.error }, 402);

  // No file named — describe what this reference entitles the buyer to.
  if (!file) {
    return json({
      item: check.key,
      title: check.item.title,
      email: check.email,
      files: check.item.files,
    });
  }

  // A reference unlocks only the files of the item it paid for.
  if (!check.item.files.includes(file)) {
    return json({ error: "That file is not part of this purchase." }, 403);
  }

  const object = await env.TEMPLATES.get(file);
  if (!object) return json({ error: "File not found. Please contact support." }, 404);

  const ext = file.split(".").pop();
  return new Response(object.body, {
    headers: {
      "Content-Type": MIME[ext] || "application/octet-stream",
      "Content-Disposition": `attachment; filename="${file}"`,
      "Cache-Control": "private, no-store",
    },
  });
}
