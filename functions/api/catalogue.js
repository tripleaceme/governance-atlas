// GET /api/catalogue -> { key: { title, price, files } }
//
// Public price list. Reading it is harmless; the point of serving it rather
// than hard-coding prices in the page is that the storefront can never quote a
// price the checkout would not honour.

import { CATALOGUE, CURRENCY, json } from "../_lib/catalogue.js";

export async function onRequestGet() {
  const out = {};
  for (const [key, item] of Object.entries(CATALOGUE)) {
    out[key] = { title: item.title, price: item.price, currency: CURRENCY, files: item.files };
  }
  return new Response(JSON.stringify(out), {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "public, max-age=300",
    },
  });
}
