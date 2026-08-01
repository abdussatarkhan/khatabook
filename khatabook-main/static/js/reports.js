(function () {
  "use strict";

  const startInput = document.getElementById("rangeStart");
  const endInput = document.getElementById("rangeEnd");
  const totalCredit = document.getElementById("totalCredit");
  const totalDebit = document.getElementById("totalDebit");
  const chartEmpty = document.getElementById("chartEmpty");
  const canvas = document.getElementById("trendChart");

  let chart = null;

  function defaultRange() {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 29);
    return [toISO(start), toISO(end)];
  }
  function toISO(d) {
    const off = d.getTimezoneOffset();
    return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10);
  }

  const [defStart, defEnd] = defaultRange();
  startInput.value = defStart;
  endInput.value = defEnd;

  function formatMoney(n) {
    return Number(n).toLocaleString(window.CURRENCY_LOCALE || "en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function formatLabel(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(window.CURRENCY_LOCALE || "en-IN", { day: "numeric", month: "short" });
  }

  async function loadData() {
    const params = new URLSearchParams({ start: startInput.value, end: endInput.value });
    const res = await fetch("/api/reports/data?" + params.toString());
    const data = await res.json();

    totalCredit.textContent = window.CURRENCY_SYMBOL + formatMoney(data.total_credit);
    totalDebit.textContent = window.CURRENCY_SYMBOL + formatMoney(data.total_debit);

    if (!data.labels.length) {
      canvas.classList.add("hidden");
      chartEmpty.classList.remove("hidden");
      if (chart) { chart.destroy(); chart = null; }
      return;
    }
    canvas.classList.remove("hidden");
    chartEmpty.classList.add("hidden");

    const labels = data.labels.map(formatLabel);

    if (chart) chart.destroy();
    chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          { label: "You gave", data: data.credit, backgroundColor: "#D14343", borderRadius: 4 },
          { label: "You got", data: data.debit, backgroundColor: "#1B8A4A", borderRadius: 4 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } },
          tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${window.CURRENCY_SYMBOL}${formatMoney(ctx.parsed.y)}` } },
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 } } },
          y: { beginAtZero: true, ticks: { font: { size: 10 } } },
        },
      },
    });
  }

  startInput.addEventListener("change", loadData);
  endInput.addEventListener("change", loadData);
  loadData();
})();
