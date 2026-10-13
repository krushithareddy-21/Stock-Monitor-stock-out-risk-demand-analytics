/* Fetch real, filtered API results and render them with Chart.js. */
const chartInstances = {};
const numberFormat = new Intl.NumberFormat();
const riskColors = { High: "#d76a5d", Medium: "#e8ae4d", Low: "#5aa47b" };
const palette = ["#347956", "#78a986", "#e5af62", "#7796ba", "#c88475", "#8a79ae", "#67a9a0"];

const elements = {
  store: document.getElementById("store-filter"),
  category: document.getElementById("category-filter"),
  region: document.getElementById("region-filter"),
  startDate: document.getElementById("start-date-filter"),
  endDate: document.getElementById("end-date-filter"),
  error: document.getElementById("dashboard-error"),
  riskBody: document.getElementById("risk-table-body"),
};

function formatNumber(value) {
  return numberFormat.format(Math.round(Number(value) || 0));
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function showError(message) {
  elements.error.textContent = message;
  elements.error.hidden = false;
}

function clearError() {
  elements.error.hidden = true;
  elements.error.textContent = "";
}

function currentQuery() {
  const parameters = new URLSearchParams();
  const values = {
    store_id: elements.store.value,
    category: elements.category.value,
    region: elements.region.value,
    start_date: elements.startDate.value,
    end_date: elements.endDate.value,
  };
  Object.entries(values).forEach(([key, value]) => {
    if (value) parameters.set(key, value);
  });
  return parameters.toString();
}

async function fetchJson(endpoint, query = currentQuery()) {
  const suffix = query ? `?${query}` : "";
  const response = await fetch(`/api/${endpoint}${suffix}`);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `The ${endpoint} request failed.`);
  }
  return payload;
}

function setSelectOptions(select, values, placeholder, selectedValue = "") {
  select.replaceChildren(new Option(placeholder, ""));
  values.forEach((value) => select.add(new Option(value, value)));
  select.value = selectedValue;
}

function updateMetric(summary, id, value) {
  document.getElementById(id).textContent = formatNumber(value);
}

function renderSummary(summary) {
  updateMetric(summary, "metric-products", summary.total_products);
  updateMetric(summary, "metric-sold", summary.total_units_sold);
  updateMetric(summary, "metric-inventory", summary.total_inventory);
  updateMetric(summary, "metric-ordered", summary.total_units_ordered);
  document.getElementById("metric-demand").textContent =
    numberFormat.format(Number(summary.average_demand_forecast || 0));
  updateMetric(summary, "metric-high-risk", summary.high_risk_products);
  document.getElementById("last-updated").textContent =
    `Updated ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function drawChart(canvasId, config) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
  const canvas = document.getElementById(canvasId);
  chartInstances[canvasId] = new Chart(canvas, {
    ...config,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...config.options,
      plugins: {
        legend: { display: false },
        ...config.options?.plugins,
      },
    },
  });
}

function barChart(canvasId, labels, datasets, options = {}) {
  drawChart(canvasId, {
    type: "bar",
    data: { labels, datasets },
    options: {
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#7b887f", font: { size: 10 } } },
        y: { beginAtZero: true, grid: { color: "#edf1ed" }, ticks: { color: "#7b887f", font: { size: 10 } } },
      },
      ...options,
    },
  });
}

function renderCategoryChart(data) {
  const labels = data.map((row) => row.Category);
  barChart("sales-category-chart", labels, [{
    label: "Units sold",
    data: data.map((row) => row.units_sold),
    backgroundColor: "#347956",
    borderRadius: 5,
    maxBarThickness: 38,
  }]);
  barChart("inventory-category-chart", labels, [{
    label: "Inventory",
    data: data.map((row) => row.inventory_level),
    backgroundColor: "#78a986",
    borderRadius: 5,
    maxBarThickness: 38,
  }]);
}

function renderDemandChart(data) {
  barChart("demand-chart", data.map((row) => row.Category), [
    {
      label: "Demand forecast",
      data: data.map((row) => row.demand_forecast),
      backgroundColor: "#e5af62",
      borderRadius: 4,
      maxBarThickness: 30,
    },
    {
      label: "Units sold",
      data: data.map((row) => row.units_sold),
      backgroundColor: "#347956",
      borderRadius: 4,
      maxBarThickness: 30,
    },
  ], { plugins: { legend: { display: true, position: "bottom", labels: { usePointStyle: true, boxWidth: 7 } } } });
}

function renderStoreCharts(stores) {
  const labels = stores.map((row) => row["Store ID"]);
  barChart("store-inventory-chart", labels, [{
    label: "Inventory",
    data: stores.map((row) => row.inventory_level),
    backgroundColor: "#7796ba",
    borderRadius: 5,
    maxBarThickness: 34,
  }]);
  barChart("store-sales-chart", labels, [{
    label: "Units sold",
    data: stores.map((row) => row.units_sold),
    backgroundColor: "#347956",
    borderRadius: 5,
    maxBarThickness: 34,
  }]);
}

function renderRisk(data) {
  drawChart("risk-chart", {
    type: "doughnut",
    data: {
      labels: data.distribution.map((item) => item.risk),
      datasets: [{
        data: data.distribution.map((item) => item.count),
        backgroundColor: data.distribution.map((item) => riskColors[item.risk] || "#aab3ad"),
        borderWidth: 0,
        hoverOffset: 5,
      }],
    },
    options: {
      cutout: "69%",
      plugins: {
        legend: { display: true, position: "bottom", labels: { usePointStyle: true, boxWidth: 7, padding: 17 } },
      },
    },
  });

  if (!data.items.length) {
    elements.riskBody.innerHTML = '<tr><td colspan="7" class="empty-cell">No stock records match these filters.</td></tr>';
    document.getElementById("risk-item-count").textContent = "0 items";
    return;
  }
  elements.riskBody.innerHTML = data.items.map((item) => {
    const riskClass = `risk-${String(item.risk).toLowerCase()}`;
    return `<tr>
      <td><span class="risk-badge ${riskClass}">${escapeHtml(item.risk)}</span></td>
      <td>${escapeHtml(item.product_id)}</td>
      <td>${escapeHtml(item.store_id)}</td>
      <td>${escapeHtml(item.category)}</td>
      <td>${formatNumber(item.inventory_level)}</td>
      <td>${formatNumber(item.demand_forecast)}</td>
      <td><span class="recommendation-badge">${escapeHtml(item.recommendation)}</span></td>
    </tr>`;
  }).join("");
  document.getElementById("risk-item-count").textContent =
    `Showing ${data.items.length} of ${formatNumber(data.distribution.reduce((total, item) => total + item.count, 0))} items`;
}

async function refreshDashboard() {
  clearError();
  const query = currentQuery();
  try {
    const [summary, categories, stores, demand, risk] = await Promise.all([
      fetchJson("summary", query),
      fetchJson("categories", query),
      fetchJson("stores", query),
      fetchJson("demand", query),
      fetchJson("risk", query),
    ]);
    renderSummary(summary);
    renderCategoryChart(categories);
    renderStoreCharts(stores);
    renderDemandChart(demand);
    renderRisk(risk);
  } catch (error) {
    showError(`Dashboard data could not be loaded: ${error.message}`);
  }
}

async function initializeDashboard() {
  try {
    const options = await fetchJson("filters", "");
    setSelectOptions(elements.store, options.stores, "All stores");
    setSelectOptions(elements.category, options.categories, "All categories");
    setSelectOptions(elements.region, options.regions, "All regions");
    elements.startDate.min = options.min_date;
    elements.startDate.max = options.max_date;
    elements.endDate.min = options.min_date;
    elements.endDate.max = options.max_date;
    await refreshDashboard();
  } catch (error) {
    showError(`Dashboard could not connect to the Flask API: ${error.message}`);
  }
}

[elements.store, elements.category, elements.region, elements.startDate, elements.endDate]
  .forEach((control) => control.addEventListener("change", refreshDashboard));

document.getElementById("reset-filters").addEventListener("click", () => {
  elements.store.value = "";
  elements.category.value = "";
  elements.region.value = "";
  elements.startDate.value = "";
  elements.endDate.value = "";
  refreshDashboard();
});

initializeDashboard();
