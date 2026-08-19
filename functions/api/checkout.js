// POST /api/checkout  { item, email }  ->  { authorization_url, reference }
//
// Starts a Paystack transaction. The price is looked up server-side from the
// catalogue rather than taken from the request, so the amount charged cannot be
// altered by editing the page.
//
// Required environment (Cloudflare Pages → Settings → Environment variables):
//   PAYSTACK_SECRET_KEY   secret, server-side only — never expose to the browser

import { CATALOGUE, CURRENCY, json } from "../_lib/catalogue.js";

export async function onRequestPost({ request, env }) {
  if (!env.PAYSTACK_SECRET_KEY) {
    return json({ error: "Payments are not configured yet." }, 503);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Expected a JSON body." }, 400);
  }

  const item = CATALOGUE[body.item];
  if (!item) {
    return json({ error: "Unknown item." }, 400);
  }

  const email = String(body.email || "").trim();
  // Deliberately loose: the authoritative check is Paystack's, and a rejected
  // address there is a clearer error than a regex quibble here.
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ error: "A valid email address is required — it is where the download link goes." }, 400);
  }

  const origin = new URL(request.url).origin;
  const reference = `ga_${body.item}_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`;

  const res = await fetch("https://api.paystack.co/transaction/initialize", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.PAYSTACK_SECRET_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      amount: item.price,
      currency: CURRENCY,
      reference,
      callback_url: `${origin}/download?ref=${reference}`,
      metadata: {
        item: body.item,
        title: item.title,
        custom_fields: [
          { display_name: "Template", variable_name: "template", value: item.title },
        ],
      },
    }),
  });

  const payload = await res.json().catch(() => ({}));
  if (!res.ok || !payload.status) {
    return json({ error: payload.message || "Could not start the payment." }, 502);
  }

  return json({
    authorization_url: payload.data.authorization_url,
    reference: payload.data.reference,
  });
}
