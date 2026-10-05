import { continueRender, delayRender, staticFile } from "remotion";

// Font disimpan setempat dalam public/fonts (Poppins & DM Serif Display, Google Fonts, lesen OFL)
const FACES: [string, string, string][] = [
  ["FireaSans", "Poppins-500.woff2", "500"],
  ["FireaSans", "Poppins-600.woff2", "600"],
  ["FireaSans", "Poppins-700.woff2", "700"],
  ["FireaSans", "Poppins-800.woff2", "800"],
  ["FireaSerif", "DMSerifDisplay-400.woff2", "400"],
];
if (typeof document !== "undefined") {
  const handle = delayRender("Memuat font");
  Promise.all(
    FACES.map(([fam, file, weight]) =>
      new FontFace(fam, `url(${staticFile(`fonts/${file}`)}) format("woff2")`, { weight }).load().then((ff) => document.fonts.add(ff)),
    ),
  ).then(() => continueRender(handle));
}
export const sans = "FireaSans, sans-serif";
export const serif = "FireaSerif, serif";

// Peranan warna (diambil daripada label Firea)
export const C = {
  cream: "#FBF4F1",   // latar asas
  blush: "#F6DCE4",   // latar babak lembut
  rose: "#E3A0B6",    // aksen sekunder / bentuk
  maroon: "#7A1C3A",  // warna jenama: tajuk, pil, CTA
  deep: "#4A0F24",    // latar penutup
  ink: "#2A1A20",     // teks badan
  aqua: "#5DB8D0",    // KHAS untuk peluh/air
  odour: "#A8964A",   // KHAS untuk bau/bakteria
  white: "#FFFFFF",
};

// Teks CTA (disahkan klien)
export const CTA = { line: "Dapatkan Sekarang" };
