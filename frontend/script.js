const API_URL = "https://ai-powered-product-analysis-comparison.onrender.com";

const form = document.getElementById("advisorForm");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const themeToggle = document.getElementById("themeToggle");
const HISTORY_KEY = "product_search_history";
const WISHLIST_KEY = "product_wishlist";
const ALERTS_KEY = "price_alerts";
const REPORTS_KEY = "saved_reports";

function saveSearch(product, budget, category, compareWith, compareWith2) {
  let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];

  history.unshift({
    product,
    budget,
    category,
    compareWith,
    compareWith2,
    timestamp: Date.now(),
  });

  history = history.slice(0, 8);

  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));

  renderHistory();
}

function renderHistory() {
  const historyWrap = document.getElementById("historyWrap");
  const historyList = document.getElementById("historyList");

  let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];

  if (history.length === 0) {
    historyWrap.style.display = "none";
    return;
  }

  historyWrap.style.display = "block";

  historyList.innerHTML = "";

  history.forEach((item, index) => {
    const div = document.createElement("div");

    div.className = "history-item";

div.innerHTML = `
<div class="history-content">
    <div class="history-product">
        ${item.product}
    </div>

    <div class="history-meta">
        <span>₹${item.budget}</span>

        <span class="history-category">
            ${item.category}
        </span>
    </div>

    <div class="history-time">
        ${new Date(item.timestamp).toLocaleString()}
    </div>
</div>

<button class="history-delete">
    ✕
</button>
`;
    const deleteBtn = div.querySelector(".history-delete");

    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteHistory(index);
    });
    div.querySelector(".history-content").addEventListener("click", () => {
      document.getElementById("productInput").value = item.product;
      document.getElementById("budgetInput").value = item.budget;
      document.getElementById("categorySelect").value = item.category;
      document.getElementById("compareInput").value = item.compareWith || "";
      document.getElementById("compareSecondInput").value = item.compareWith2 || "";
    });

    historyList.appendChild(div);
  });
}

function deleteHistory(index) {
  let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];

  history.splice(index, 1);

  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));

  renderHistory();
}
function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function formatCurrency(value, currency = "INR") {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "Price unavailable";

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeList(items, fallback) {
  if (Array.isArray(items) && items.length) return items;
  return fallback ? [fallback] : [];
}

function scorePercent(value) {
  const score = Number(value);
  if (!Number.isFinite(score)) return 0;
  return clamp(score * 10, 0, 100);
}

function listTemplate(items) {
  const list = normalizeList(items, "No details available.");
  return `<ul>${list.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function showMessage(title, message, type = "info") {
  result.innerHTML = `
    <article class="notice ${type}">
      <h2>${escapeHtml(title)}</h2>
      <p>${escapeHtml(message)}</p>
    </article>
  `;
}

function renderScores(scores = {}) {
  const entries = Object.entries(scores);
  if (!entries.length) return "";

  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Scorecard</span>
        <h2>Category ratings</h2>
      </div>
      <div class="score-grid">
        ${entries
          .map(([key, value]) => {
            const pct = scorePercent(value);
            const label = key.replaceAll("_", " ");
            return `
            <div class="score">
              <div class="score-top">
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(value)}/10</strong>
              </div>
              <div class="bar" aria-hidden="true">
                <span style="width:${pct}%"></span>
              </div>
            </div>
          `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderFeatures(features = []) {
  if (!Array.isArray(features) || !features.length) return "";

  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Details</span>
        <h2>Important features</h2>
      </div>
      <div class="feature-grid">
        ${features
          .map(
            (feature) => `
          <article class="feature">
            <strong>${escapeHtml(feature.name || "Feature")}</strong>
            <p>${escapeHtml(feature.value || "No description available.")}</p>
          </article>
        `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function marketplaceLinks(product) {
  const query = encodeURIComponent(product);
  return `
    <div class="buy-buttons">
      <a href="https://www.amazon.in/s?k=${query}" target="_blank" rel="noopener" class="buy-btn amazon">Buy on Amazon</a>
      <a href="https://www.flipkart.com/search?q=${query}" target="_blank" rel="noopener" class="buy-btn flipkart">Buy on Flipkart</a>
      <button id="downloadPdfBtn" class="pdf-btn" type="button">Download PDF</button>
    </div>
  `;
}

function renderPriceHistory(priceHistory = {}) {
  const badge = priceHistory.deal_badge || "unknown";
  return `
    <section class="section-card price-history-card">
      <div class="section-heading">
        <span class="kicker">Price history</span>
        <h2>${escapeHtml(priceHistory.deal_status || "Deal status unavailable")}</h2>
      </div>
      <p>${escapeHtml(priceHistory.deal_message || "Check seller listings before buying.")}</p>
      <div class="price-history-grid">
        <span><strong>${formatCurrency(priceHistory.current_price)}</strong><small>Current price</small></span>
        <span><strong>${formatCurrency(priceHistory.historical_low)}</strong><small>Historical low</small></span>
        <span><strong>${formatCurrency(priceHistory.historical_average)}</strong><small>Typical price</small></span>
        <span><strong>${formatCurrency(priceHistory.historical_high)}</strong><small>Historical high</small></span>
      </div>
      <div class="deal-badge ${escapeHtml(badge)}">${escapeHtml(priceHistory.source || "Price source unavailable")} · ${escapeHtml(priceHistory.confidence || "unknown")}</div>
    </section>
  `;
}

function featureValue(product, featureName) {
  const features = Array.isArray(product.features) ? product.features : [];
  const match = features.find(
    (feature) => String(feature.name || "").toLowerCase() === featureName.toLowerCase(),
  );
  return match?.value || "Check listing";
}

function renderThreeWayComparison(data) {
  const products = (data.comparison_products || []).filter(Boolean).slice(0, 3);
  if (products.length < 2) return renderComparison(data, products[0]?.name || "", "");

  const featureNames = Array.from(
    new Set(
      products.flatMap((product) =>
        Array.isArray(product.features)
          ? product.features.map((feature) => feature.name).filter(Boolean)
          : [],
      ),
    ),
  ).slice(0, 6);

  const rows = [
    {
      label: "Current price",
      values: products.map((product) => formatCurrency(product.price || product.estimated_price)),
    },
    {
      label: "Deal alert",
      values: products.map((product) => product.price_history?.deal_status || "Unavailable"),
    },
    {
      label: "Best for",
      values: products.map((product) => product.best_for || "General buyers"),
    },
    ...featureNames.map((name) => ({
      label: name,
      values: products.map((product) => featureValue(product, name)),
    })),
  ];

  return `
    <section class="section-card comparison-table-card">
      <div class="section-heading">
        <span class="kicker">Comparison</span>
        <h2>${products.length}-way side-by-side table</h2>
      </div>
      ${data.head_to_head?.verdict ? `<p class="muted">${escapeHtml(data.head_to_head.verdict)}</p>` : ""}
      <div class="comparison-table-wrap">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Factor</th>
              ${products.map((product) => `<th>${escapeHtml(product.name || "Product")}</th>`).join("")}
            </tr>
          </thead>
          <tbody>
            ${rows
              .map(
                (row) => `
                  <tr>
                    <td>${escapeHtml(row.label)}</td>
                    ${row.values.map((value) => `<td>${escapeHtml(value)}</td>`).join("")}
                  </tr>
                `,
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderComparison(data, product, compareWith) {
  if (!compareWith || !data.comparison) return "";

  const comparison = data.comparison;
  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Comparison</span>
        <h2>${escapeHtml(product)} vs ${escapeHtml(compareWith)}</h2>
      </div>
      <p class="muted">${escapeHtml(comparison.summary || "No comparison summary available.")}</p>
      <div class="two-column">
        <article class="mini-card positive">
          <h3>Better in</h3>
          ${listTemplate(comparison.better_in)}
        </article>
        <article class="mini-card negative">
          <h3>Weaker in</h3>
          ${listTemplate(comparison.weaker_in)}
        </article>
      </div>
    </section>
  `;
}

function renderAlternatives(alternatives = [], alternative = "") {
  const items = normalizeList(alternatives, alternative).filter(Boolean);
  if (!items.length) return "";

  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Alternatives</span>
        <h2>Other options to consider</h2>
      </div>
      <div class="pill-list">
        ${items.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
      </div>
    </section>
  `;
}

function productInitial(product) {
  const firstLetter = String(product || "B")
    .trim()
    .charAt(0)
    .toUpperCase();
  return firstLetter || "B";
}

function getStoredList(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) || [];
  } catch {
    return [];
  }
}
function setStoredList(key, items) {
  localStorage.setItem(key, JSON.stringify(items));
}

function renderMiniChart(points = [], label = "Price history") {
  if (!points.length) return `<p class="muted">No chart data available.</p>`;
  const width = 640;
  const height = 190;
  const prices = points.map((point) => Number(point.price)).filter(Number.isFinite);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = Math.max(max - min, 1);
  const coords = points.map((point, index) => {
    const x = points.length === 1 ? 0 : (index / (points.length - 1)) * width;
    const y = height - ((Number(point.price) - min) / range) * (height - 22) - 10;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  return `
    <div class="chart-box" role="img" aria-label="${escapeHtml(label)}">
      <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <polyline points="${coords.join(" ")}" fill="none" stroke="currentColor" stroke-width="4" vector-effect="non-scaling-stroke"></polyline>
      </svg>
      <div class="chart-meta">
        <span>Low ${formatCurrency(min)}</span>
        <span>High ${formatCurrency(max)}</span>
      </div>
    </div>
  `;
}

function renderSmartDashboard(data) {
  const intel = data.intelligence || {};
  const advice = intel.purchase_advice || {};
  const forecast = intel.price_forecast || {};
  const cheapest = intel.cheapest_store || {};

  return `
    <section class="section-card smart-dashboard">
      <div class="section-heading">
        <span class="kicker">Smart price intelligence</span>
        <h2>${escapeHtml(advice.recommendation || "Buy timing unavailable")}</h2>
      </div>
      <div class="dashboard-grid">
        <span><strong>${formatCurrency(data.price)}</strong><small>Current Price</small></span>
        <span><strong>${formatCurrency(data.price_history?.historical_low)}</strong><small>Lowest Ever Price</small></span>
        <span><strong>${formatCurrency(data.price_history?.historical_high)}</strong><small>Highest Ever Price</small></span>
        <span><strong>${escapeHtml(intel.deal_score ?? "N/A")}/100</strong><small>Deal Score</small></span>
        <span><strong>${escapeHtml(forecast.trend || "Stable")}</strong><small>Price Trend</small></span>
        <span><strong>${formatCurrency(forecast.thirty_day)}</strong><small>30-Day Prediction</small></span>
        <span><strong>${escapeHtml(advice.recommendation || "Review")}</strong><small>Best Time To Buy</small></span>
        <span><strong>${escapeHtml(cheapest.store || "Unknown")}</strong><small>Cheapest Store</small></span>
        <span><strong>${formatCurrency(advice.estimated_savings)}</strong><small>Expected Savings</small></span>
      </div>
      <p>${escapeHtml(advice.reason || "Use the full analysis before deciding.")}</p>
    </section>
  `;
}

function renderPriceCharts(data) {
  const intel = data.intelligence || {};
  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Price tracking</span>
        <h2>30-day and 90-day price history</h2>
      </div>
      <div class="chart-grid">
        <article>
          <h3>30-day history</h3>
          ${renderMiniChart(intel.price_points_30, "30-day price history")}
        </article>
        <article>
          <h3>90-day history</h3>
          ${renderMiniChart(intel.price_points_90, "90-day price history")}
        </article>
      </div>
    </section>
  `;
}

function renderSellerComparison(data) {
  const stores = data.intelligence?.store_prices || [];
  if (!stores.length) return "";

  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Competitor prices</span>
        <h2>Store-wise price comparison</h2>
      </div>
      <div class="comparison-table-wrap">
        <table class="comparison-table">
          <thead>
            <tr><th>Seller</th><th>Price</th><th>Rating</th><th>Availability</th><th>Link</th></tr>
          </thead>
          <tbody>
            ${stores.map((store) => `
              <tr class="${store.is_cheapest ? "winner-row" : ""}">
                <td>${escapeHtml(store.store)}${store.is_cheapest ? " · Cheapest" : ""}</td>
                <td>${formatCurrency(store.price)}</td>
                <td>${escapeHtml(store.rating || "N/A")}</td>
                <td>${escapeHtml(store.availability || "Unknown")}</td>
                <td><a href="${escapeHtml(store.url)}" target="_blank" rel="noopener">Open</a></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderForecasts(data) {
  const forecast = data.intelligence?.price_forecast || {};
  const advice = data.intelligence?.purchase_advice || {};
  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Price prediction</span>
        <h2>Future price drop forecast</h2>
      </div>
      <div class="dashboard-grid compact">
        <span><strong>${formatCurrency(forecast.seven_day)}</strong><small>7-day forecast</small></span>
        <span><strong>${formatCurrency(forecast.thirty_day)}</strong><small>30-day forecast</small></span>
        <span><strong>${formatCurrency(forecast.ninety_day)}</strong><small>90-day forecast</small></span>
        <span><strong>${formatCurrency(advice.expected_discounted_price)}</strong><small>Expected sale price</small></span>
        <span><strong>${formatCurrency(advice.estimated_savings)}</strong><small>Estimated savings</small></span>
      </div>
      <p>${escapeHtml(forecast.analysis || "Forecast unavailable.")}</p>
    </section>
  `;
}

function renderSpecTable(data) {
  const specs = data.intelligence?.spec_table || [];
  if (!specs.length) return "";

  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Specifications</span>
        <h2>Product specification table</h2>
      </div>
      <div class="comparison-table-wrap">
        <table class="comparison-table spec-table">
          <tbody>
            ${specs.map((spec) => `<tr><td>${escapeHtml(spec.name)}</td><td>${escapeHtml(spec.value)}</td></tr>`).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderValueScores(data) {
  const scores = data.intelligence?.value_scores || {};
  const entries = Object.entries(scores);
  if (!entries.length) return "";

  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">AI value score</span>
        <h2>Score breakdown</h2>
      </div>
      <div class="score-grid">
        ${entries.map(([key, value]) => `
          <div class="score">
            <div class="score-top">
              <span>${escapeHtml(key.replaceAll("_", " "))}</span>
              <strong>${escapeHtml(value)}/100</strong>
            </div>
            <div class="bar" aria-hidden="true"><span style="width:${clamp(Number(value), 0, 100)}%"></span></div>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}

function renderReviewsAndRatings(data) {
  const reviews = data.intelligence?.review_analysis || {};
  const ratings = data.intelligence?.ratings || {};
  const distribution = ratings.distribution || {};
  return `
    <section class="insight-grid">
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Review analysis</span>
          <h2>Buyer sentiment</h2>
        </div>
        <div class="dashboard-grid compact">
          <span><strong>${escapeHtml(reviews.positive_percent ?? "N/A")}%</strong><small>Positive reviews</small></span>
          <span><strong>${escapeHtml(reviews.negative_percent ?? "N/A")}%</strong><small>Negative reviews</small></span>
        </div>
        <h3>Common complaints</h3>
        ${listTemplate(reviews.common_complaints)}
        <h3>Most liked features</h3>
        ${listTemplate(reviews.most_liked_features)}
      </article>
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Ratings</span>
          <h2>Marketplace ratings</h2>
        </div>
        <div class="dashboard-grid compact">
          <span><strong>${escapeHtml(ratings.amazon ?? "N/A")}</strong><small>Amazon</small></span>
          <span><strong>${escapeHtml(ratings.flipkart ?? "N/A")}</strong><small>Flipkart</small></span>
          <span><strong>${escapeHtml(ratings.overall ?? "N/A")}</strong><small>Overall</small></span>
        </div>
        ${Object.entries(distribution).map(([stars, pct]) => `
          <div class="rating-row"><span>${escapeHtml(stars)} star</span><div class="bar"><span style="width:${clamp(Number(pct), 0, 100)}%"></span></div><small>${escapeHtml(pct)}%</small></div>
        `).join("")}
      </article>
    </section>
  `;
}

function renderRecommendations(data) {
  const recs = data.budget_recommendations || {};
  const trending = data.trending_products || {};
  return `
    <section class="insight-grid">
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Budget recommendations</span>
          <h2>Best options around your budget</h2>
        </div>
        <div class="pill-list">
          <span>Under budget: ${escapeHtml(recs.best_under_budget || "Unavailable")}</span>
          <span>Premium: ${escapeHtml(recs.premium_option || "Unavailable")}</span>
          <span>Value: ${escapeHtml(recs.value_option || "Unavailable")}</span>
          <span>Budget: ${escapeHtml(recs.budget_option || "Unavailable")}</span>
        </div>
      </article>
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Trending products</span>
          <h2>Popular searches</h2>
        </div>
        ${listTemplate([
          ...(trending.top_phones || []).map((item) => `Phone: ${item}`),
          ...(trending.top_laptops || []).map((item) => `Laptop: ${item}`),
          ...(trending.top_smartwatches || []).map((item) => `Watch: ${item}`),
          ...(trending.top_headphones || []).map((item) => `Headphones: ${item}`),
        ].slice(0, 8))}
      </article>
    </section>
  `;
}

function renderAvailabilitySaleAndRefurb(data) {
  const availability = data.intelligence?.availability || [];
  const refurb = data.intelligence?.refurbished || {};
  const saleCalendar = data.sale_calendar || [];
  return `
    <section class="insight-grid">
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Availability</span>
          <h2>Stock status</h2>
        </div>
        ${listTemplate(availability.map((item) => `${item.store}: ${item.status}`))}
        <h3>Refurbished vs new</h3>
        <p>New: ${formatCurrency(refurb.new_price)} · Refurbished: ${formatCurrency(refurb.refurbished_price)} · Savings: ${formatCurrency(refurb.savings)}</p>
        <p>${escapeHtml(refurb.recommendation || "")}</p>
      </article>
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Sale calendar</span>
          <h2>Upcoming deal windows</h2>
        </div>
        ${listTemplate(saleCalendar.map((sale) => `${sale.name}: ${sale.window}, ${sale.expected_discount}`))}
      </article>
    </section>
  `;
}

function renderActionCenter(data, values) {
  return `
    <section class="section-card action-center">
      <div class="section-heading">
        <span class="kicker">Tools</span>
        <h2>Save, alert, share, export</h2>
      </div>
      <div class="action-grid">
        <button type="button" class="tool-btn" id="wishlistBtn">Save to Wishlist</button>
        <label class="target-price-field">
          <span>Target price</span>
          <input id="targetPriceInput" inputmode="numeric" placeholder="${Math.max(1, Math.round(Number(data.price || values.budget) * 0.9))}" />
        </label>
        <button type="button" class="tool-btn" id="setAlertBtn">Set Price Alert</button>
        <button type="button" class="tool-btn" id="notifyBtn">Enable Browser Alerts</button>
        <button type="button" class="tool-btn" id="copyLinkBtn">Copy Link</button>
        <button type="button" class="tool-btn" id="whatsappShareBtn">WhatsApp</button>
        <button type="button" class="tool-btn" id="telegramShareBtn">Telegram</button>
        <button type="button" class="tool-btn" id="emailShareBtn">Email</button>
        <button type="button" class="tool-btn" id="saveReportBtn">Save Report</button>
        <button type="button" class="tool-btn" id="exportPngBtn">Export PNG</button>
        <button type="button" class="tool-btn" id="exportJpegBtn">Export JPEG</button>
      </div>
    </section>
  `;
}

function renderUserDashboard() {
  const searches = getStoredList(HISTORY_KEY);
  const wishlist = getStoredList(WISHLIST_KEY);
  const alerts = getStoredList(ALERTS_KEY);
  const reports = getStoredList(REPORTS_KEY);
  return `
    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">User dashboard</span>
        <h2>Your activity</h2>
      </div>
      <div class="dashboard-grid compact">
        <span><strong>${searches.length}</strong><small>Total searches</small></span>
        <span><strong>${wishlist.length}</strong><small>Wishlist count</small></span>
        <span><strong>${reports.length}</strong><small>Saved reports</small></span>
        <span><strong>${alerts.length}</strong><small>Price alerts</small></span>
      </div>
      <h3>Wishlist</h3>
      ${listTemplate(wishlist.map((item) => item.product))}
      <h3>Alert management</h3>
      ${listTemplate(alerts.map((item) => `${item.product}: target ${formatCurrency(item.targetPrice)}`))}
    </section>
  `;
}

function enhanceReport(data, values) {
  const anchor = result.querySelector(".price-history-card") || result.querySelector(".result-hero");
  if (anchor) {
    anchor.insertAdjacentHTML(
      "afterend",
      [
        renderSmartDashboard(data),
        renderPriceCharts(data),
        renderSellerComparison(data),
        renderForecasts(data),
        renderSpecTable(data),
        renderValueScores(data),
        renderReviewsAndRatings(data),
        renderRecommendations(data),
        renderAvailabilitySaleAndRefurb(data),
        renderActionCenter(data, values),
        renderUserDashboard(),
      ].join(""),
    );
  }
  bindActionCenter(data, values);
}

function shareUrl(values) {
  const params = new URLSearchParams({
    product: values.product,
    budget: values.budget,
    category: values.category,
  });
  if (values.compareWith) params.set("compare", values.compareWith);
  if (values.compareWith2) params.set("compare2", values.compareWith2);
  return `${location.origin}${location.pathname}?${params.toString()}`;
}

function bindActionCenter(data, values) {
  const wishlistBtn = document.getElementById("wishlistBtn");
  const setAlertBtn = document.getElementById("setAlertBtn");
  const notifyBtn = document.getElementById("notifyBtn");
  const copyLinkBtn = document.getElementById("copyLinkBtn");
  const saveReportBtn = document.getElementById("saveReportBtn");
  const pngBtn = document.getElementById("exportPngBtn");
  const jpegBtn = document.getElementById("exportJpegBtn");
  const shareText = `${values.product} analysis: ${data.intelligence?.deal_label || data.price_history?.deal_status || "Deal review"} at ${formatCurrency(data.price)}.`;
  const url = shareUrl(values);

  wishlistBtn?.addEventListener("click", () => {
    const wishlist = getStoredList(WISHLIST_KEY).filter((item) => item.product !== values.product);
    wishlist.unshift({ product: values.product, budget: values.budget, savedAt: Date.now() });
    setStoredList(WISHLIST_KEY, wishlist.slice(0, 50));
    wishlistBtn.textContent = "Saved";
  });

  setAlertBtn?.addEventListener("click", () => {
    const targetPrice = document.getElementById("targetPriceInput")?.value || Math.round(Number(data.price || values.budget) * 0.9);
    const alerts = getStoredList(ALERTS_KEY).filter((item) => item.product !== values.product);
    alerts.unshift({ product: values.product, targetPrice, currentPrice: data.price, createdAt: Date.now() });
    setStoredList(ALERTS_KEY, alerts.slice(0, 50));
    setAlertBtn.textContent = "Alert Saved";
  });

  notifyBtn?.addEventListener("click", async () => {
    if (!("Notification" in window)) {
      notifyBtn.textContent = "Not Supported";
      return;
    }
    const permission = await Notification.requestPermission();
    notifyBtn.textContent = permission === "granted" ? "Alerts Enabled" : "Alerts Blocked";
  });

  copyLinkBtn?.addEventListener("click", async () => {
    await navigator.clipboard?.writeText(url);
    copyLinkBtn.textContent = "Copied";
  });

  document.getElementById("whatsappShareBtn")?.addEventListener("click", () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(`${shareText} ${url}`)}`, "_blank", "noopener");
  });

  document.getElementById("telegramShareBtn")?.addEventListener("click", () => {
    window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(shareText)}`, "_blank", "noopener");
  });

  document.getElementById("emailShareBtn")?.addEventListener("click", () => {
    location.href = `mailto:?subject=${encodeURIComponent(`${values.product} buying report`)}&body=${encodeURIComponent(`${shareText}\n\n${url}`)}`;
  });

  saveReportBtn?.addEventListener("click", () => {
    const reports = getStoredList(REPORTS_KEY);
    reports.unshift({ product: values.product, price: data.price, savedAt: Date.now(), verdict: data.final_verdict });
    setStoredList(REPORTS_KEY, reports.slice(0, 30));
    saveReportBtn.textContent = "Report Saved";
  });

  pngBtn?.addEventListener("click", () => exportSummaryImage(data, values, "png"));
  jpegBtn?.addEventListener("click", () => exportSummaryImage(data, values, "jpeg"));
}

function exportSummaryImage(data, values, type = "png") {
  const canvas = document.createElement("canvas");
  canvas.width = 1200;
  canvas.height = 720;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = type === "jpeg" ? "#ffffff" : "#111315";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = type === "jpeg" ? "#111315" : "#f5f7fa";
  ctx.font = "bold 42px Arial";
  ctx.fillText("Budget Product Advisor", 60, 80);
  ctx.font = "bold 34px Arial";
  ctx.fillText(values.product, 60, 145);
  ctx.font = "26px Arial";
  [
    `Current price: ${formatCurrency(data.price)}`,
    `Deal score: ${data.intelligence?.deal_score ?? "N/A"}/100 (${data.intelligence?.deal_label || "N/A"})`,
    `Recommendation: ${data.intelligence?.purchase_advice?.recommendation || "Review"}`,
    `Cheapest store: ${data.intelligence?.cheapest_store?.store || "Unknown"}`,
    `Expected savings: ${formatCurrency(data.intelligence?.purchase_advice?.estimated_savings)}`,
  ].forEach((line, index) => ctx.fillText(line, 60, 220 + index * 52));
  ctx.font = "22px Arial";
  ctx.fillText(String(data.final_verdict || data.overview || "").slice(0, 120), 60, 560);
  const link = document.createElement("a");
  link.download = `${values.product.replace(/[^\w-]+/g, "_")}.${type === "jpeg" ? "jpg" : "png"}`;
  link.href = canvas.toDataURL(type === "jpeg" ? "image/jpeg" : "image/png", 0.92);
  link.click();
}

function renderResult(data, values) {
  const price = Number(data.price || data.price_history?.current_price);
  const budget = Number(values.budget);
  const hasPrice = Number.isFinite(price) && price > 0;
  const hasBudget = Number.isFinite(budget) && budget > 0;
  const budgetPct =
    hasPrice && hasBudget
      ? clamp(Math.round((price / budget) * 100), 0, 999)
      : null;
  const image =
    data.image && String(data.image).startsWith("http") ? data.image : "";
  const verdict =
    data.final_verdict ||
    data.buying_advice ||
    data.alternative ||
    "Review the details below before buying.";
  const priceLabel = data.price_confidence === "live" ? "Current live price" : "Estimated price";

  result.innerHTML = `
      ${
        data.category_warning
          ? `
        <article class="notice warning">
          <h2>Category adjusted</h2>
          <p>${escapeHtml(data.category_warning)}</p>
        </article>
      `
          : ""
      }

      <section class="result-hero">
        <div class="product-media">
          ${
            image
              ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(values.product)} product image" onerror="this.parentElement.classList.add('image-missing'); this.remove();" />`
              : ""
          }
          <div class="image-fallback" aria-hidden="true">
            <span>${escapeHtml(productInitial(values.product))}</span>
            <small>No image available</small>
          </div>
        </div>
        <div class="verdict-card">
          <span class="kicker">Final verdict</span>
          <h2>${escapeHtml(values.product)}</h2>
          <p>${escapeHtml(verdict)}</p>
  <div class="buy-buttons">
  <a
    href="https://www.amazon.in/s?k=${encodeURIComponent(values.product)}"
    target="_blank"
    class="buy-btn amazon"
  >
    🛒 Buy on Amazon
  </a>

  <a
    href="https://www.flipkart.com/search?q=${encodeURIComponent(values.product)}"
    target="_blank"
    class="buy-btn flipkart"
  >
    🛒 Buy on Flipkart
  </a>
  <button id="downloadPdfBtn" class="pdf-btn">
    📄 Download PDF
</button>
</div>
        <div class="meta-grid">
          <span><strong>${escapeHtml(data.detected_category || values.category)}</strong><small>Category</small></span>
          <span><strong>${hasPrice ? formatCurrency(price, data.currency || "INR") : "Unavailable"}</strong><small>${escapeHtml(priceLabel)}</small></span>
          <span><strong>${formatCurrency(values.budget, "INR")}</strong><small>Your budget</small></span>
        </div>
    
    </section>

    <section class="section-card">
      <div class="section-heading">
        <span class="kicker">Overview</span>
        <h2>Quick purchase read</h2>
      </div>
      <p>${escapeHtml(data.overview || "No overview available.")}</p>
      <div class="budget-meter">
        <div class="meter-copy">
          <strong>${budgetPct === null ? "Budget fit unavailable" : `${budgetPct}% of budget`}</strong>
          <span>${escapeHtml(data.budget_fit || "Price fit is based on the estimated market price.")}</span>
        </div>
        <div class="meter" aria-hidden="true"><span style="width:${budgetPct === null ? 0 : clamp(budgetPct, 0, 100)}%"></span></div>
      </div>
    </section>

    <section class="insight-grid">
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Pros</span>
          <h2>Why it works</h2>
        </div>
        ${listTemplate(data.pros)}
      </article>
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Cons</span>
          <h2>Tradeoffs</h2>
        </div>
        ${listTemplate(data.cons)}
      </article>
    </section>

    ${renderScores(data.scores)}
    ${renderFeatures(data.features)}

    <section class="insight-grid">
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Best for</span>
          <h2>Recommended use</h2>
        </div>
        <p>${escapeHtml(data.best_for || "General buyers.")}</p>
      </article>
      <article class="section-card">
        <div class="section-heading">
          <span class="kicker">Avoid if</span>
          <h2>Not ideal for</h2>
        </div>
        <p>${escapeHtml(data.not_recommended_for || "No major avoid case provided.")}</p>
      </article>
    </section>

    ${
      data.bullets?.length
        ? `
      <section class="section-card">
        <div class="section-heading">
          <span class="kicker">Summary</span>
          <h2>Key points</h2>
        </div>
        ${listTemplate(data.bullets)}
      </section>
    `
        : ""
    }


    ${renderThreeWayComparison(data)}
    ${renderAlternatives(data.alternatives, data.alternative)}
  `;

   const hero = result.querySelector(".result-hero");
   if (hero && data.price_history) {
      hero.insertAdjacentHTML("afterend", renderPriceHistory(data.price_history));
   }

   enhanceReport(data, values);

   const amazonBtn = result.querySelector(".buy-btn.amazon");
   const flipkartBtn = result.querySelector(".buy-btn.flipkart");
   const pdfBtn = document.getElementById("downloadPdfBtn");

   if (amazonBtn) {
      amazonBtn.textContent = "Buy on Amazon";
      amazonBtn.setAttribute("rel", "noopener");
   }

   if (flipkartBtn) {
      flipkartBtn.textContent = "Buy on Flipkart";
      flipkartBtn.setAttribute("rel", "noopener");
   }

   if (pdfBtn) {
      pdfBtn.textContent = "Download PDF";
      pdfBtn.type = "button";
      pdfBtn.addEventListener("click", () => {
         downloadPDF(data, values);
      });
   }
}

async function explainProduct(event) {
  event?.preventDefault();

  const values = {
    product: document.getElementById("productInput").value.trim(),
    compareWith: document.getElementById("compareInput").value.trim(),
    compareWith2: document.getElementById("compareSecondInput").value.trim(),
    budget: document.getElementById("budgetInput").value.trim(),
    category: document.getElementById("categorySelect").value,
  };

  if (!values.product || !values.budget) {
    showMessage(
      "Missing details",
      "Enter a product name and your budget to start.",
      "warning",
    );
    return;
  }
  saveSearch(
    values.product,
    values.budget,
    values.category,
    values.compareWith,
    values.compareWith2,
  );
  loading.classList.remove("hidden");
  result.innerHTML = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product: values.product,
        budget: values.budget,
        category: values.category,
        compare_with: [values.compareWith, values.compareWith2].filter(Boolean),
        compare_with_2: values.compareWith2,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    renderResult(data, values);
  } catch (error) {
    console.error(error);
    showMessage(
      "Backend connection failed",
      "Start the Flask backend on http://127.0.0.1:5000, then try again.",
      "error",
    );
  } finally {
    loading.classList.add("hidden");
  }
}

form.addEventListener("submit", explainProduct);

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("light");
});
window.addEventListener("load", () => {
  renderHistory();
  setupVoiceSearch();
  restoreFromUrl();
});

document.getElementById("historyClearAll").addEventListener("click", () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
});

function setupVoiceSearch() {
  const productInput = document.getElementById("productInput");
  if (!productInput || document.getElementById("voiceSearchBtn")) return;

  const button = document.createElement("button");
  button.id = "voiceSearchBtn";
  button.type = "button";
  button.className = "voice-btn";
  button.textContent = "Voice Search";
  productInput.insertAdjacentElement("afterend", button);

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    button.disabled = true;
    button.textContent = "Voice Unavailable";
    return;
  }

  button.addEventListener("click", () => {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    button.textContent = "Listening...";
    recognition.onresult = (event) => {
      productInput.value = event.results[0][0].transcript;
      button.textContent = "Voice Search";
      productInput.focus();
    };
    recognition.onerror = () => {
      button.textContent = "Try Voice Again";
    };
    recognition.onend = () => {
      if (button.textContent === "Listening...") button.textContent = "Voice Search";
    };
    recognition.start();
  });
}

function restoreFromUrl() {
  const params = new URLSearchParams(location.search);
  const product = params.get("product");
  if (!product) return;
  document.getElementById("productInput").value = product;
  document.getElementById("budgetInput").value = params.get("budget") || "";
  document.getElementById("categorySelect").value = params.get("category") || "general";
  document.getElementById("compareInput").value = params.get("compare") || "";
  document.getElementById("compareSecondInput").value = params.get("compare2") || "";
}
function downloadPDF(data, values) {

    const { jsPDF } = window.jspdf;

    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text("Budget Product Advisor Report", 20, 20);

    doc.setFontSize(14);
    doc.text(`Product: ${values.product}`, 20, 40);

    doc.text(`Budget: ₹${values.budget}`, 20, 50);

    doc.text(`Category: ${values.category}`, 20, 60);

    doc.text("Overview:", 20, 80);
    doc.text(data.overview || "N/A", 20, 90, {
        maxWidth: 170
    });

    doc.text("Final Verdict:", 20, 130);
    doc.text(data.final_verdict || "N/A", 20, 140, {
        maxWidth: 170
    });

    doc.save(`${values.product}.pdf`);
}

function downloadPDF(data, values) {
    if (!window.jspdf?.jsPDF) {
      showMessage("PDF unavailable", "The PDF library did not load. Check your internet connection and try again.", "error");
      return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const margin = 16;
    const maxWidth = 178;
    let y = 18;

    const addPageIfNeeded = (height = 10) => {
      if (y + height > 282) {
        doc.addPage();
        y = 18;
      }
    };

    const addHeading = (text) => {
      addPageIfNeeded(14);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(13);
      doc.text(text, margin, y);
      y += 8;
    };

    const addText = (text) => {
      const lines = doc.splitTextToSize(String(text || "N/A"), maxWidth);
      addPageIfNeeded(lines.length * 6 + 2);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.text(lines, margin, y);
      y += lines.length * 6 + 3;
    };

    const addList = (label, items) => {
      addHeading(label);
      normalizeList(items, "No details available.").forEach((item) => addText(`- ${item}`));
    };

    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("Budget Product Advisor Report", margin, y);
    y += 12;

    addText(`Product: ${values.product}`);
    addText(`Budget: ${formatCurrency(values.budget)}`);
    addText(`Category: ${data.detected_category || values.category}`);
    addText(`Price: ${formatCurrency(data.price || data.price_history?.current_price)} (${data.price_confidence || "unknown"})`);

    addHeading("Deal Alert");
    addText(data.price_history?.deal_message || "Price history unavailable.");

    addHeading("Overview");
    addText(data.overview);

    addList("Pros", data.pros);
    addList("Cons", data.cons);

    addHeading("Important Features");
    (data.features || []).forEach((feature) => addText(`${feature.name}: ${feature.value}`));

    if ((data.comparison_products || []).length > 1) {
      addHeading("Comparison");
      (data.comparison_products || []).slice(0, 3).forEach((product) => {
        addText(`${product.name}: ${formatCurrency(product.price || product.estimated_price)} - ${product.price_history?.deal_status || "Deal status unavailable"}`);
      });
    }

    addHeading("Final Verdict");
    addText(data.final_verdict || data.buying_advice || "Review the full analysis before buying.");

    doc.save(`${values.product.replace(/[^\w-]+/g, "_")}_report.pdf`);
}
