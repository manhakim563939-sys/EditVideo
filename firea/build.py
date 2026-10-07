"""Bina index.html tunggal (gambar + suara dibenam) dari firea.html untuk upload ke Netlify."""
import base64, pathlib, re
here = pathlib.Path(__file__).parent
src = (here / "firea.html").read_text()
b64 = lambda p: base64.b64encode((here / p).read_bytes()).decode()

src = re.sub(r'src="(img/[^"]+\.jpg)"',
             lambda m: f'src="data:image/jpeg;base64,{b64(m.group(1))}"' if (here / m.group(1)).exists() else m.group(0), src)
src = src.replace('<audio id="vo-audio" src="audio/voiceover.mp3" preload="metadata"></audio>',
                  '<audio id="vo-audio" preload="metadata"></audio>')
audio_js = f'<script>document.getElementById("vo-audio").src="data:audio/mpeg;base64,{b64("audio/voiceover-48k.mp3")}";</script>'

title, body = src.split("\n", 1)
head = f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{title}
<meta name="description" content="Firea Celeste Musk, deodoran roll-on 0% alkohol untuk wanita bertudung yang aktif. Kering dari pagi sampai malam. Bernotifikasi KKM NOT260705867K.">
<link rel="canonical" href="https://fireadeodorant.com/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://fireadeodorant.com/">
<meta property="og:title" content="Firea Celeste Musk | Ketiak Berpeluh, Dah Tak Risau Lagi">
<meta property="og:description" content="Deodoran roll-on 0% alkohol untuk wanita bertudung yang aktif. Kering dari pagi sampai malam. COD tersedia.">
<meta property="og:image" content="https://fireadeodorant.com/img/produk-pink.jpg">
<meta name="theme-color" content="#5a1531">
</head>
<body>
'''
(here / "index.html").write_text(head + body + "\n" + audio_js + "\n</body>\n</html>\n")
print("index.html", round((here / "index.html").stat().st_size / 1e6, 2), "MB")
