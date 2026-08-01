(function () {
  "use strict";

  // ---------------- Search ----------------
  const searchInput = document.getElementById("customerSearch");
  const rows = Array.from(document.querySelectorAll(".customer-row"));
  const noResults = document.getElementById("noSearchResults");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      const q = searchInput.value.trim().toLowerCase();
      let visibleCount = 0;
      rows.forEach((row) => {
        const match = row.dataset.name.includes(q);
        row.classList.toggle("hidden", !match);
        if (match) visibleCount++;
      });
      if (noResults) {
        noResults.classList.toggle("hidden", !(q && visibleCount === 0));
      }
    });
  }

  // ---------------- Add customer sheet ----------------
  const backdrop = document.getElementById("addCustomerBackdrop");
  const fab = document.getElementById("addCustomerFab");
  const cancelBtn = document.getElementById("cancelAddCustomer");
  const form = document.getElementById("addCustomerForm");
  const errorEl = document.getElementById("addCustomerError");

  function openSheet() {
    backdrop.classList.remove("hidden");
    document.getElementById("newCustomerName").focus();
  }
  function closeSheet() {
    backdrop.classList.add("hidden");
    form.reset();
    errorEl.classList.add("hidden");
  }

  if (fab) fab.addEventListener("click", openSheet);
  if (cancelBtn) cancelBtn.addEventListener("click", closeSheet);
  if (backdrop) {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeSheet();
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("newCustomerName").value.trim();
      const phone = document.getElementById("newCustomerPhone").value.trim();
      const submitBtn = form.querySelector('button[type="submit"]');

      submitBtn.disabled = true;
      try {
        const res = await fetch("/api/customers", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.CSRF_TOKEN,
          },
          body: JSON.stringify({ name, phone }),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Could not add customer.");
        }
        window.location.href = "/customer/" + data.id;
      } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove("hidden");
        submitBtn.disabled = false;
      }
    });
  }
})();
