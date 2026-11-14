// Harga & postage Firea (mesti sama dengan CONFIG dalam firea.html dan shop.html).
export const PACKAGES = { 1: 35, 2: 55, 3: 69 };
export const EAST_SHIPPING = 15; // Sabah, Sarawak, Labuan. Semenanjung percuma.
export const STATES = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang", "Perak", "Perlis", "Pulau Pinang", "Selangor", "Terengganu", "WP Kuala Lumpur", "WP Putrajaya", "Sabah", "Sarawak", "WP Labuan"];
export const isEast = negeri => /Sabah|Sarawak|Labuan/.test(negeri);

export function quote(qty, negeri) {
  const price = PACKAGES[qty];
  if (!price || !STATES.includes(negeri)) return null;
  const pos = isEast(negeri) ? EAST_SHIPPING : 0;
  return { qty, price, pos, jumlah: price + pos };
}

export function normMobile(t) {
  let d = String(t || "").replace(/\D/g, "");
  if (d.startsWith("0")) d = "6" + d;
  else if (d && !d.startsWith("6")) d = "60" + d;
  return d;
}
