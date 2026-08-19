// Product catalogue — the single source of truth for what is sold and for how
// much. Mirrored from templates/build.py; keep the two in step.
//
// Prices are in kobo because that is the unit Paystack charges in. They are
// defined server-side on purpose: the browser sends only an item key, never a
// price, so a tampered request cannot buy a document for less than it costs.

export const CATALOGUE = {
  "dpa": {
    title: "Data Processing Agreement",
    price: 500000,
    files: ["dpa.docx", "dpa.pdf"],
  },
  "ropa": {
    title: "Records of Processing Activities (RoPA)",
    price: 500000,
    files: ["ropa.docx", "ropa.pdf"],
  },
  "dpia": {
    title: "Data Protection Impact Assessment (DPIA)",
    price: 750000,
    files: ["dpia.docx", "dpia.pdf"],
  },
  "risk-assessment": {
    title: "Data Risk Assessment",
    price: 500000,
    files: ["risk-assessment.docx", "risk-assessment.pdf"],
  },
  "transfer-risk-assessment": {
    title: "Cross-Border Transfer Risk Assessment",
    price: 750000,
    files: ["transfer-risk-assessment.docx", "transfer-risk-assessment.pdf"],
  },
  "retention-schedule": {
    title: "Data Retention Schedule",
    price: 350000,
    files: ["retention-schedule.docx", "retention-schedule.pdf"],
  },
  "dsr-log": {
    title: "Data Subject Request Log",
    price: 350000,
    files: ["dsr-log.docx", "dsr-log.pdf"],
  },
  "bundle": {
    title: "The complete set — all seven templates",
    price: 2500000,
    files: ["governance-atlas-templates.zip"],
  },
};

export const CURRENCY = "NGN";

export function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
    },
  });
}
