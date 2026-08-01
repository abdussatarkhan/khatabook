(function () {
  "use strict";

  const customerId = document.getElementById("ledger").dataset.customerId;
  const ledger = document.getElementById("ledger");
  const balanceBar = document.getElementById("balanceBar");
  const balanceValue = document.getElementById("balanceValue");

  // ---------------- Add transaction sheet ----------------
  const txBackdrop = document.getElementById("txBackdrop");
  const txForm = document.getElementById("txForm");
  const txTitle = document.getElementById("txSheetTitle");
  const txTypeInput = document.getElementById("txType");
  const txAmount = document.getElementById("txAmount");
  const txNote = document.getElementById("txNote");
  const txDate = document.getElementById("txDate");
  const txError = document.getElementById("txError");
  const cancelTx = document.getElementById("cancelTx");

  function todayISO() {
    const d = new Date();
    const off = d.getTimezoneOffset();
    return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10);
  }

  function openTxSheet(type) {
    txTypeInput.value = type;
    txTitle.textContent = type === "credit" ? "You gave" : "You got";
    txDate.value = todayISO();
    txError.classList.add("hidden");
    txBackdrop.classList.remove("hidden");
    setTimeout(() => txAmount.focus(), 50);
  }
  function closeTxSheet() {
    txBackdrop.classList.add("hidden");
    txForm.reset();
  }

  document.getElementById("btnYouGave").addEventListener("click", () => openTxSheet("credit"));
  document.getElementById("btnYouGot").addEventListener("click", () => openTxSheet("debit"));
  cancelTx.addEventListener("click", closeTxSheet);
  txBackdrop.addEventListener("click", (e) => { if (e.target === txBackdrop) closeTxSheet(); });

  txForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById("txSubmit");
    submitBtn.disabled = true;

    try {
      const res = await fetch(`/api/customers/${customerId}/transactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": window.CSRF_TOKEN,
        },
        body: JSON.stringify({
          type: txTypeInput.value,
          amount: txAmount.value,
          note: txNote.value,
          date: txDate.value,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not save entry.");

      appendLedgerEntry(data);
      updateBalance(data.new_balance_rupees);
      closeTxSheet();
    } catch (err) {
      txError.textContent = err.message;
      txError.classList.remove("hidden");
    } finally {
      submitBtn.disabled = false;
    }
  });

  function appendLedgerEntry(tx) {
    const emptyState = ledger.querySelector(".empty-state");
    if (emptyState) emptyState.remove();

    const entry = document.createElement("div");
    entry.className = `ledger-entry ledger-entry--${tx.type}`;
    entry.dataset.txId = tx.id;
    entry.innerHTML = `
      <div class="ledger-entry__bubble">
        <span class="ledger-entry__label">${tx.type === "credit" ? "You gave" : "You got"}</span>
        <span class="ledger-entry__amount">${window.CURRENCY_SYMBOL}${formatMoney(tx.amount_rupees)}</span>
        ${tx.note ? `<span class="ledger-entry__note">${escapeHtml(tx.note)}</span>` : ""}
        <span class="ledger-entry__meta">${tx.date}</span>
      </div>`;
    ledger.appendChild(entry);
    entry.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  function updateBalance(newBalance) {
    balanceBar.classList.remove("is-get", "is-give", "is-settled");
    const label = balanceBar.querySelector("span");
    if (newBalance > 0) {
      balanceBar.classList.add("is-get");
      label.textContent = "You'll get";
      balanceValue.textContent = window.CURRENCY_SYMBOL + formatMoney(newBalance);
    } else if (newBalance < 0) {
      balanceBar.classList.add("is-give");
      label.textContent = "You'll give";
      balanceValue.textContent = window.CURRENCY_SYMBOL + formatMoney(-newBalance);
    } else {
      balanceBar.classList.add("is-settled");
      label.textContent = "Settled up";
      balanceValue.textContent = window.CURRENCY_SYMBOL + "0.00";
    }
  }

  function formatMoney(n) {
    return Number(n).toLocaleString(window.CURRENCY_LOCALE || "en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  // ---------------- Reminder sheet ----------------
  const reminderBtn = document.getElementById("reminderBtn");
  const reminderBackdrop = document.getElementById("reminderBackdrop");
  const reminderPreview = document.getElementById("reminderPreview");
  const reminderWaBtn = document.getElementById("reminderWaBtn");
  const cancelReminder = document.getElementById("cancelReminder");

  reminderBtn.addEventListener("click", async () => {
    reminderBackdrop.classList.remove("hidden");
    reminderPreview.textContent = "Preparing message…";
    reminderWaBtn.classList.add("hidden");

    try {
      const res = await fetch(`/api/customers/${customerId}/reminder`, {
        method: "POST",
        headers: { "X-CSRFToken": window.CSRF_TOKEN },
      });
      const data = await res.json();
      reminderPreview.textContent = data.message;
      reminderWaBtn.href = data.wa_link;
      reminderWaBtn.classList.remove("hidden");
      if (!data.has_phone) {
        reminderWaBtn.textContent = "Copy message (no phone saved)";
        reminderWaBtn.removeAttribute("href");
        reminderWaBtn.addEventListener("click", (e) => {
          e.preventDefault();
          navigator.clipboard?.writeText(data.message);
        }, { once: true });
      }
    } catch (err) {
      reminderPreview.textContent = "Could not prepare the reminder. Please try again.";
    }
  });
  cancelReminder.addEventListener("click", () => reminderBackdrop.classList.add("hidden"));
  reminderBackdrop.addEventListener("click", (e) => { if (e.target === reminderBackdrop) reminderBackdrop.classList.add("hidden"); });
})();
