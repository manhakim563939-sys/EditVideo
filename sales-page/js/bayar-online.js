/* Order Jus Bidara Hitam: COD / DuitNow QR terus di website (tanpa WhatsApp), dan Billplz bila diaktifkan.
   Event Pixel InitiateCheckout + Purchase dihantar HANYA selepas server sahkan order diterima. */
(function () {
  const track = (ev, data, id) => { try { if (window.fbq) fbq("track", ev, data || {}, id ? { eventID: id } : undefined); } catch (_) {} };

  /* Billplz (bayar online automatik) */
  window.JBH_bayarOnline = async function (order, btn) {
    const label = btn ? btn.innerHTML : "";
    if (btn) { btn.disabled = true; btn.innerHTML = "Menyediakan bayaran…"; }
    try {
      const res = await fetch("/api/create-bill", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(order) });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.url) throw new Error(data.error || "Tak dapat sediakan bayaran sekarang. Cuba lagi atau pilih COD.");
      track("InitiateCheckout", { currency: "MYR", value: Number(data.jumlah) || 0, num_items: Number(order.pkg) }, "ic-" + data.id);
      try { localStorage.setItem("jbh-pending-order", JSON.stringify({ ...order, jumlah: data.jumlah, billId: data.id, at: Date.now() })); } catch (_) {}
      location.href = data.url;
    } catch (e) {
      if (btn) { btn.disabled = false; btn.innerHTML = label; }
      throw e;
    }
  };

  /* COD / DuitNow: hantar order ke server, rekod event, terus ke halaman pesanan */
  window.JBH_hantarOrder = async function (order, btn) {
    const label = btn ? btn.innerHTML : "";
    if (btn) { btn.disabled = true; btn.innerHTML = "Menghantar pesanan…"; }
    try {
      const res = await fetch("/api/order-notify", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(order) });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.orderId) throw new Error(data.error || "Tak dapat hantar pesanan sekarang.");
      const saved = { ...order, ...data, at: Date.now() };
      try { localStorage.setItem("jbh-order-" + data.orderId, JSON.stringify(saved)); localStorage.setItem("jbh-last-order", data.orderId); } catch (_) {}
      // Sekali sahaja bagi setiap order (eventID sama walaupun pelanggan tekan dua kali)
      let first = true;
      try { first = !localStorage.getItem("jbh-tracked-" + data.orderId); localStorage.setItem("jbh-tracked-" + data.orderId, "1"); } catch (_) {}
      if (first && !data.pendua) {
        const ev = { currency: "MYR", value: Number(data.jumlah) || 0, content_name: data.pakej, num_items: Number(order.pkg), content_type: "product" };
        track("InitiateCheckout", ev, "ic-" + data.orderId);
        if (data.bayar === "COD") track("Purchase", ev, "p-" + data.orderId); // DuitNow: Purchase selepas resit dihantar
      }
      location.href = "/pesanan/?id=" + encodeURIComponent(data.orderId) + "#" + data.token;
    } catch (e) {
      if (btn) { btn.disabled = false; btn.innerHTML = label; }
      throw e;
    }
  };

  /* Pesanan DuitNow belum selesai (pelanggan keluar ke app bank): tunjuk butang sambung */
  try {
    const last = localStorage.getItem("jbh-last-order");
    const lo = last && JSON.parse(localStorage.getItem("jbh-order-" + last) || "null");
    const fresh = lo && Date.now() - (lo.at || 0) < 3 * 24 * 3600e3;
    if (fresh && lo.bayar === "DUITNOW" && !localStorage.getItem("jbh-paid-" + last) && !localStorage.getItem("jbh-receipt-" + last)) {
      const bar = document.createElement("a");
      bar.href = "/pesanan/?id=" + encodeURIComponent(last) + "#" + lo.token;
      bar.textContent = "⏳ Pesanan " + last + " (RM" + lo.jumlah + ") belum selesai. Dah bayar? Tekan sini";
      bar.style.cssText = "position:fixed;left:0;right:0;top:0;z-index:9999;display:block;background:#d6245c;color:#fff;font:700 14px Poppins,system-ui,sans-serif;text-align:center;padding:12px 16px;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.25)";
      document.body.appendChild(bar);
    }
  } catch (_) {}

  /* Sorok pilihan Billplz sehingga kunci disediakan di Netlify */
  const opts = [...document.querySelectorAll('input[name="bayar"][value="ONLINE"]')].map(i => i.closest("label"));
  opts.forEach(l => { if (l) l.hidden = true; });
  fetch("/api/pay-status", { cache: "no-store" })
    .then(r => (r.ok ? r.json() : { online: false }))
    .catch(() => ({ online: false }))
    .then(s => { if (s && s.online) opts.forEach(l => { if (l) l.hidden = false; }); });
})();
