// frontend/script.js
function setPercent(el, pct) {
  el.style.width = Math.max(0, Math.min(100, pct)) + "%";
}

async function explainProduct() {
  const product = document.getElementById("productInput").value.trim();
  const compareWith = document.getElementById("compareInput").value.trim();
  const budget = document.getElementById("budgetInput").value.trim();
  const category = document.getElementById("categorySelect").value;

  if (!product || !budget) {
    alert("Enter product and budget.");
    return;
  }

  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  loading.classList.remove("hidden");
  result.innerHTML = "";

  try {
    const resp = await fetch("http://127.0.0.1:5000/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product,
        budget,
        category,
        compare_with: compareWith,
      }),
    });

    const data = await resp.json();
    loading.classList.add("hidden");

    // Build UI
    const overview = data.overview || "No overview";
    const pros = data.pros || [];
    const cons = data.cons || [];
    const bullets = data.bullets || [];
    const alternative = data.alternative || "";
    const alternatives = data.alternatives || [];
    const scores = data.scores || { performance: 0, battery: 0, value: 0 };
    const price = data.price || null;
    const currency = data.currency || "INR";
    const image = data.image || null;
    const compare_price = data.compare_price || null;
    const category_advice = data.category_advice || "";

    // row cards
    const row = document.createElement("div");
    row.className = "row-cards";

    const cardOverview = document.createElement("div");
    cardOverview.className = "card";
    cardOverview.innerHTML = `<h3>📦 Overview</h3><p>${overview}</p>`;
    row.appendChild(cardOverview);

    const cardPros = document.createElement("div");
    cardPros.className = "card";
    cardPros.innerHTML = `<h3>👍 Pros</h3><ul>${pros
      .map((p) => `<li>${p}</li>`)
      .join("")}</ul>`;
    row.appendChild(cardPros);

    const cardCons = document.createElement("div");
    cardCons.className = "card";
    cardCons.innerHTML = `<h3>👎 Cons</h3><ul>${cons
      .map((c) => `<li>${c}</li>`)
      .join("")}</ul>`;
    row.appendChild(cardCons);

    result.appendChild(row);

    // price row with image and bar
    const priceRow = document.createElement("div");
    priceRow.className = "price-row";

    const imgBox = document.createElement("div");
    imgBox.className = "product-image";

    // ----------- FIXED IMAGE CODE (NO 404) -----------
// FINAL FIX — LOCAL IMAGE FALLBACK
// --- FINAL FIX: REAL IMAGE + LOCAL FALLBACK ---
let safeImage = image && image.startsWith("http")
  ? image
  : "assets/no-image.png";


imgBox.innerHTML = `
  <img src="${safeImage}"
       alt="product image"
       style="width:100%;height:100%;object-fit:cover;border-radius:10px;"
       onerror="this.src='assets/no-image.png'">
`;


    // --------------------------------------------------

    priceRow.appendChild(imgBox);

    const priceBox = document.createElement("div");
    priceBox.className = "price-box";
    let priceHTML = `<h4>Price Info</h4>`;

    if (price) {
      priceHTML += `<div style="font-size:20px;font-weight:600">${currency} ${price.toLocaleString()}</div>`;
      const pct = Math.round((price / Number(budget)) * 100);
      priceHTML += `<div class="price-bar"><div id="priceFill" class="price-fill"></div></div>`;
      priceHTML += `<div style="margin-top:8px;color:var(--muted)">${pct}% of your budget</div>`;
    } else {
      priceHTML += `<div style="color:var(--muted)">Price not found (web fetch failed)</div>`;
    }

    if (compare_price) {
      priceHTML += `<div style="margin-top:8px;color:var(--muted)">
        Compare product price: ${data.compare_currency || "INR"} ${compare_price}
      </div>`;
    }

    priceBox.innerHTML = priceHTML;
    priceRow.appendChild(priceBox);
    result.appendChild(priceRow);

    // animate price fill
    setTimeout(() => {
      const fill = document.getElementById("priceFill");
      if (fill) {
        const pct = price ? Math.round((price / Number(budget)) * 100) : 0;
        setPercent(fill, Math.min(100, pct));
      }
    }, 50);

// ---- SCORES ----
const scoreBox = document.createElement("div");
scoreBox.className = "card";
scoreBox.style.marginTop = "12px";

let scoreHTML = `<h3>📊 Scores</h3><div class="scores">`;

Object.keys(scores).forEach(key => {
  const pct = (Number(scores[key]) || 0) * 10;

  scoreHTML += `
    <div class="score">
      <div>${key.replace("_", " ").toUpperCase()}</div>
      <div class="bar"><div class="inner" style="width:${pct}%"></div></div>
    </div>
  `;
});

scoreHTML += `</div>`;
scoreBox.innerHTML = scoreHTML;
result.appendChild(scoreBox);

// animate dynamically
// setTimeout(() => {
//   scoreKeys.forEach(key => {
//     const bar = document.getElementById(`${key}Inner`);
//     if (bar) {
//       const val = Math.min(100, (Number(scores[key]) || 0) * 10);
//       bar.style.width = val + "%";
//     }
//   });
// }, 80);


    // bullets summary
    if (bullets.length) {
      const bulletsCard = document.createElement("div");
      bulletsCard.className = "card";
      bulletsCard.innerHTML = `<h3>📝 Quick bullets</h3>
        <div class="bullets">${bullets
          .map((b) => `<div>• ${b}</div>`)
          .join("")}</div>`;
      result.appendChild(bulletsCard);
    }

    // category advice
    if (category_advice) {
      const advice = document.createElement("div");
      advice.className = "card";
      advice.innerHTML = `<h3>🧭 Category Advice</h3><p>${category_advice}</p>`;
      result.appendChild(advice);
    }

    // alternatives
    if (alternatives && alternatives.length) {
      const altCard = document.createElement("div");
      altCard.className = "card";
      altCard.innerHTML = `<h3>🔄 Alternatives</h3>
        <div class="alternatives">
          ${alternatives.map((a) => `<div class="alt-card"><h4>${a}</h4></div>`).join("")}
        </div>`;
      result.appendChild(altCard);
    }

    if (alternative) {
      const altSingle = document.createElement("div");
      altSingle.className = "card";
      altSingle.innerHTML = `<h3>✅ Recommendation</h3><p>${alternative}</p>`;
      result.appendChild(altSingle);
    }
  // ---- COMPARISON CARD (A vs B) ----
if (compareWith && data.comparison) {

    const comp = data.comparison;

    const compCard = document.createElement("div");
    compCard.className = "card";

    compCard.innerHTML = `
      <h3>⚔️ Comparison: ${product} vs ${compareWith}</h3>

      <p style="color:var(--muted)">
        ${comp.summary || "No comparison summary available."}
      </p>

      <div style="display:flex; gap:20px; flex-wrap:wrap; margin-top:10px">

        <div style="flex:1">
          <h4 style="color:#00d1b2; margin:0 0 6px 0">✔ Better In</h4>
          <ul>
            ${(comp.better_in || []).length 
              ? comp.better_in.map(i => `<li>${i}</li>`).join("")
              : "<li>No strong advantages found.</li>"
            }
          </ul>
        </div>

        <div style="flex:1">
          <h4 style="color:#ff7b7b; margin:0 0 6px 0">✖ Weaker In</h4>
          <ul>
            ${(comp.weaker_in || []).length
              ? comp.weaker_in.map(i => `<li>${i}</li>`).join("")
              : "<li>No weaknesses detected.</li>"
            }
          </ul>
        </div>

      </div>
    `;

    result.appendChild(compCard);
}



  } catch (err) {
    loading.classList.add("hidden");
    alert("Backend error. Check console.");
    console.error(err);
  }
}
