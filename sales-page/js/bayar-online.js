/* Bayar online melalui Billplz: simpan order dalam telefon pelanggan, cipta bil di server, terus ke halaman bayaran. */
window.JBH_bayarOnline = async function (order, btn) {
  const label = btn ? btn.innerHTML : "";
  if (btn) { btn.disabled = true; btn.innerHTML = "Menyediakan bayaran…"; }
  try {
    const res = await fetch("/api/create-bill", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(order),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.url) throw new Error(data.error || "Tak dapat sediakan bayaran sekarang. Cuba lagi atau pilih COD.");
    try { localStorage.setItem("jbh-pending-order", JSON.stringify({ ...order, jumlah: data.jumlah, billId: data.id, at: Date.now() })); } catch (_) {}
    location.href = data.url;
  } catch (e) {
    if (btn) { btn.disabled = false; btn.innerHTML = label; }
    throw e;
  }
};

/* Sorok pilihan "Bayar online" sehingga Billplz disediakan (atau bila fungsi server tiada). */
(function () {
  const opts = [...document.querySelectorAll('input[name="bayar"][value="ONLINE"]')].map(i => i.closest("label"));
  opts.forEach(l => { if (l) l.hidden = true; });
  fetch("/api/pay-status", { cache: "no-store" })
    .then(r => (r.ok ? r.json() : { online: false }))
    .catch(() => ({ online: false }))
    .then(s => { if (s && s.online) opts.forEach(l => { if (l) l.hidden = false; }); });
})();
