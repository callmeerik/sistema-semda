document.addEventListener("DOMContentLoaded", function () {
  console.log("Dashboard JS ejecutado");
  console.log(window.dashboardData);

  const datos = window.dashboardData;

  // numero de entregas por mes
  Plotly.newPlot(
    "grafico-entregas",
    [{
      x: datos.entregasLabels,
      y: datos.entregasValues,
      type: "bar",
      marker: { color: "#22c55e" }
    }],
    {
      paper_bgcolor: "#020617",
      plot_bgcolor: "#020617",
      font: { color: "#e5e7eb" }
    },
    { responsive: true }
  );

  // numero de donaciones por cada categoria
  Plotly.newPlot(
    "grafico-categorias",
    [{
      labels: datos.categoriasLabels,
      values: datos.categoriasValues,
      type: "pie",
      marker: {
        colors: ["#38bdf8", "#a855f7", "#f97316", "#22c55e", "#ef4444"]
      }
    }],
    {
      paper_bgcolor: "#020617",
      font: { color: "#e5e7eb" }
    },
    { responsive: true }
  );
});
