"""Bina folder website Firea untuk upload ke Netlify.

firea.html -> index.html        (fireadeodorant.com)
shop.html  -> shop/index.html   (fireadeodorant.com/shop/)
Gambar, suara dan video kekal sebagai fail berasingan (img/, audio/, media/) supaya page ringan.
Jalankan: python3 build.py  ->  ../output/fireadeodorant-website.zip (folder "fireadeodorant")
"""
import pathlib, re, shutil, zipfile

here = pathlib.Path(__file__).parent
PIXEL_ID = "2090608328226528"   # Firea Pixel (Meta). Kosongkan "" untuk matikan.
PIXEL = f'''<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
''' if PIXEL_ID else ""
OUT_ZIP = here.parent / "output" / "fireadeodorant-website.zip"

def head(title, desc, url, og_title, og_desc, og_type="website", color="#5a1531"):
    return f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{title}
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="https://fireadeodorant.com/img/produk-pink.jpg">
<meta name="theme-color" content="{color}">
{PIXEL}</head>
<body>
'''

def page(src_name, prefix, **meta):
    src = (here / src_name).read_text()
    if prefix:
        src = re.sub(r'(src|poster)="(img|audio|media)/', lambda m: f'{m.group(1)}="{prefix}{m.group(2)}/', src)
    title, body = src.split("\n", 1)
    return head(title, **meta) + body + "\n</body>\n</html>\n"

def assets(html):
    return sorted(set(re.findall(r'(?:src|poster)="(?:\.\./)?((?:img|audio|media)/[^"]+)"', html)))

if __name__ == "__main__":
    index = page("firea.html", "",
                 desc="Firea Celeste Musk, deodoran roll-on 0% alkohol untuk wanita bertudung yang aktif. Kering dari pagi sampai malam. Bernotifikasi KKM NOT260705867K.",
                 url="https://fireadeodorant.com/", og_title="Firea Celeste Musk | Ketiak Berpeluh, Dah Tak Risau Lagi",
                 og_desc="Deodoran roll-on 0% alkohol untuk wanita bertudung yang aktif. Kering dari pagi sampai malam. COD tersedia.")
    shop = page("shop.html", "../",
                desc="Firea Celeste Musk Deodorant Roll-on 50ml. 0% alkohol, cepat kering, tahan pagi sampai malam. COD & free pos 2 botol (Semenanjung).",
                url="https://fireadeodorant.com/shop/", og_title="Firea Celeste Musk Deodorant Roll-on 50ml | Dari RM28",
                og_desc="0% alkohol, cepat kering, tak melekit. COD tersedia. Free pos 2 botol ke atas (Semenanjung).",
                og_type="product", color="#7d1f45")
    (here / "index.html").write_text(index)
    (here / "shop").mkdir(exist_ok=True)
    (here / "shop" / "index.html").write_text(shop)

    files = sorted(set(assets(index)) | set(assets(shop)) | {"img/produk-pink.jpg"})
    missing = [f for f in files if not (here / f).exists()]
    if missing:
        raise SystemExit("Fail tiada: " + ", ".join(missing))
    OUT_ZIP.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(here / "index.html", "fireadeodorant/index.html")
        z.write(here / "shop" / "index.html", "fireadeodorant/shop/index.html")
        for f in files:
            z.write(here / f, f"fireadeodorant/{f}", compress_type=zipfile.ZIP_STORED if f.endswith((".mp4", ".mp3", ".jpg")) else zipfile.ZIP_DEFLATED)
    print(f"index.html {len(index)/1e3:.0f} KB, shop/index.html {len(shop)/1e3:.0f} KB, {len(files)} fail aset")
    print("zip:", OUT_ZIP, f"{OUT_ZIP.stat().st_size/1e6:.1f} MB")
