const btn = document.getElementById("run");
const results = document.getElementById("results");
const statusEl = document.getElementById("status");

const money = (value) =>
  "₦" + Number(value).toLocaleString("en-NG", { maximumFractionDigits: 0 });

const items = [
  {
    sku: "DESK-001",
    product_name: "AeroDesk Pro Standing Desk",
    our_price: 449000,
    competitor: "Nova Retail",
    url: location.origin + "/demo/alpha.html",
  },
  {
    sku: "AUDIO-014",
    product_name: "Orbit ANC Headphones",
    our_price: 119900,
    competitor: "Vector Supply",
    url: location.origin + "/demo/bravo.html",
  },
  {
    sku: "PROJ-007",
    product_name: "Pulse Mini Projector",
    our_price: 189000,
    competitor: "HexaMart",
    url: location.origin + "/demo/charlie.html",
  },
];

btn.onclick = async () => {
  btn.disabled = true;
  btn.innerHTML = "Scanning market…";
  statusEl.textContent = "Browser automation running";
  results.className = "empty";
  results.textContent =
    "Playwright is opening competitor pages, extracting prices and stock, and capturing evidence…";

  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Scan failed");

    const rows = data.results;
    document.getElementById("critical").textContent = rows.filter(
      (item) => item.severity === "CRITICAL",
    ).length;
    const risk = rows.reduce((total, item) => total + item.opportunity, 0);
    document.getElementById("risk").textContent = money(risk);
    statusEl.textContent = `Scan #${data.scan_id} complete`;

    results.className = "grid";
    results.innerHTML = rows
      .map(
        (item) => `<div class="finding">
          <div><strong>${item.product_name}</strong><small>${item.competitor} · ${item.sku}</small></div>
          <div><small>Our price</small><strong>${money(item.our_price)}</strong></div>
          <div><small>Competitor</small><strong>${money(item.competitor_price)}</strong></div>
          <div><span class="badge ${item.severity}">${item.severity}</span><small>${item.stock === "out" ? "Out of stock" : "In stock"}</small></div>
          <div><small>Recommended action</small><strong class="recommendation">${item.recommendation}</strong></div>
          <a href="${item.screenshot}" target="_blank" rel="noopener noreferrer">Evidence ↗</a>
        </div>`,
      )
      .join("");
  } catch (error) {
    statusEl.textContent = "Scan failed";
    results.textContent = error.message;
  } finally {
    btn.disabled = false;
    btn.innerHTML = "Run live scan <span>↗</span>";
  }
};
