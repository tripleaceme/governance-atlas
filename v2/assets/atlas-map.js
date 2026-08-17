// Shared map + search behaviour. Expects MAP_DATA (from <domain>-map.js).
const STATUS_LABEL = { a: "In force", d: "In progress", n: "No comprehensive regulation" };
const CONTS = [["all","All"],["africa","Africa"],["europe","Europe"],["asia","Asia"],
               ["north-america","N. America"],["south-america","S. America"],["oceania","Oceania"]];

const slugify = n => n.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")
  .replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");

// ── search ──
const hs = document.getElementById("homesearch"), hg = document.getElementById("homesugg");
const ALL = Object.entries(MAP_DATA).map(([code, r]) => ({ code, name: r[0], slug: r[1], status: r[2], law: r[4] }));
function renderSugg() {
  const q = hs.value.trim().toLowerCase();
  hg.innerHTML = "";
  if (!q) return hg.classList.remove("show");
  const m = ALL.filter(c => c.name.toLowerCase().includes(q)).slice(0, 6);
  if (!m.length) return hg.classList.remove("show");
  m.forEach(c => {
    const b = document.createElement("button");
    b.innerHTML = '<span class="st ' + c.status + '"></span>' + c.name +
                  '<span class="slaw">' + (c.law || STATUS_LABEL[c.status]) + "</span>";
    b.addEventListener("click", () => { location.href = "countries/" + c.slug + ".html"; });
    hg.appendChild(b);
  });
  hg.classList.add("show");
}
if (hs) {
  hs.addEventListener("input", renderSugg);
  hs.addEventListener("focus", renderSugg);
  hs.addEventListener("blur", () => setTimeout(() => hg.classList.remove("show"), 180));
}

// ── map ──
const mf = document.getElementById("mapfilters"), mh = document.getElementById("maphover");
let els = [], svgEl = null, origVB = null;
const parseVB = s => s.split(/[\s,]+/).map(Number);

function animateVB(t) {
  const from = parseVB(svgEl.getAttribute("viewBox")), start = performance.now(), dur = 380;
  (function step(now) {
    const k = Math.min(1, (now - start) / dur), e = k * (2 - k);
    svgEl.setAttribute("viewBox", from.map((v, i) => v + (t[i] - v) * e).join(" "));
    if (k < 1) requestAnimationFrame(step);
  })(start);
}

function filterMap(cont) {
  let x1 = 1e9, y1 = 1e9, x2 = -1e9, y2 = -1e9, found = false;
  els.forEach(({ el, rec, label }) => {
    const inC = rec[3] === cont;
    el.classList.toggle("dimmed", cont !== "all" && !inC);
    if (label) label.classList.toggle("show", cont !== "all" && inC);
    if (inC) {
      const b = el.getBBox();
      if (b.width || b.height) {
        found = true;
        x1 = Math.min(x1, b.x); y1 = Math.min(y1, b.y);
        x2 = Math.max(x2, b.x + b.width); y2 = Math.max(y2, b.y + b.height);
      }
    }
  });
  if (!svgEl) return;
  if (cont === "all" || !found) return animateVB(origVB);
  const pad = Math.max(x2 - x1, y2 - y1) * 0.06;
  animateVB([x1 - pad, y1 - pad, (x2 - x1) + 2 * pad, (y2 - y1) + 2 * pad]);
}

if (mf) {
  CONTS.forEach(([slug, label], i) => {
    const b = document.createElement("button");
    b.className = "fbtn" + (i === 0 ? " on" : "");
    b.textContent = label;
    b.addEventListener("click", () => {
      mf.querySelectorAll(".fbtn").forEach(x => x.classList.remove("on"));
      b.classList.add("on"); filterMap(slug);
    });
    mf.appendChild(b);
  });
}

function anchorBox(el) {
  if (el.tagName.toLowerCase() === "g") {
    let best = null, bestA = 0;
    el.querySelectorAll("path").forEach(p => {
      const b = p.getBBox(), a = b.width * b.height;
      if (a > bestA) { bestA = a; best = b; }
    });
    if (best) return best;
  }
  return el.getBBox();
}

fetch("../assets/world.svg").then(r => r.text()).then(txt => {
  const wm = document.getElementById("worldmap");
  if (!wm) return;
  wm.innerHTML = txt;
  const svg = wm.querySelector("svg");
  svgEl = svg; origVB = parseVB(svg.getAttribute("viewBox"));
  svg.insertAdjacentHTML("afterbegin",
    '<defs><pattern id="hatchmap" width="5" height="5" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">' +
    '<line x1="0" y1="0" x2="0" y2="5" stroke="var(--hatch)" stroke-width="1.8"/></pattern></defs>');
  const NS = "http://www.w3.org/2000/svg";
  Object.entries(MAP_DATA).forEach(([code, rec]) => {
    const el = svg.querySelector("#" + code.toLowerCase());
    if (!el) return;
    el.classList.add("cty", "st-" + rec[2]);
    el.addEventListener("mouseenter", () => {
      mh.innerHTML = "<b>" + rec[0] + "</b> — " + STATUS_LABEL[rec[2]] + (rec[4] ? " · " + rec[4] : "");
    });
    el.addEventListener("click", () => { location.href = "countries/" + rec[1] + ".html"; });
    const b = anchorBox(el);
    const t = document.createElementNS(NS, "text");
    t.setAttribute("x", b.x + b.width / 2); t.setAttribute("y", b.y + b.height / 2);
    t.setAttribute("class", "clabel"); t.textContent = code;
    svg.appendChild(t);
    els.push({ el, rec, label: t });
  });
}).catch(() => { if (mh) mh.textContent = "Map unavailable — use the search above."; });
