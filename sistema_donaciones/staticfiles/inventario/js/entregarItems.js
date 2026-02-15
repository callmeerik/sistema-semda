document.addEventListener("DOMContentLoaded", () => {

  const origenSelect = document.getElementById("origen");
  const casaContainer = document.getElementById("casa-hogar-container");
  const casaSelect = document.getElementById("casa-hogar");
  const beneficiarioSelect = document.getElementById("beneficiario");

  function limpiarBeneficiarios() {
    beneficiarioSelect.innerHTML =
      '<option value="">Seleccione un beneficiario</option>';
  }

  // ===== ORIGEN =====
  origenSelect.addEventListener("change", () => {
    limpiarBeneficiarios();

    if (origenSelect.value === "casa") {
      casaContainer.classList.remove("hidden");
    } else {
      casaContainer.classList.add("hidden");
      casaSelect.value = "";
    }

    if (origenSelect.value === "particular") {
      window.beneficiariosParticulares.forEach(b => {
        beneficiarioSelect.innerHTML +=
          `<option value="${b.id}">${b.nombre}</option>`;
      });
    }
  });

  // ===== CASA HOGAR =====
  casaSelect.addEventListener("change", () => {
    limpiarBeneficiarios();

    const casaId = parseInt(casaSelect.value);

    window.beneficiariosCasa
      .filter(b => b.casa_id === casaId)
      .forEach(b => {
        beneficiarioSelect.innerHTML +=
          `<option value="${b.id}">${b.nombre}</option>`;
      });
  });

});
