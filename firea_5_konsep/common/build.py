"""Build one concept video.

  python common/build.py v1_angkat_tangan            -> audio + video + mux -> <v>/output/<v>_preview.mp4
  python common/build.py v1_angkat_tangan --still 3 9 -> <v>/build/still_*.png

Each <v>/video.py defines: DUR, compose(ctx, t), MUSIC (kwargs for music.arrange), cues().
"""
import importlib.util
import os
import subprocess
import sys

COMMON = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, COMMON)
import cairo  # noqa: E402

import fx  # noqa: E402
import music  # noqa: E402


def load(vdir):
    spec = importlib.util.spec_from_file_location("video", f"{vdir}/video.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def frame(mod, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, fx.W, fx.H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    mod.compose(ctx, t)
    surf.flush()
    return surf


def main():
    name = sys.argv[1].rstrip("/")
    vdir = os.path.join(os.path.dirname(COMMON), name)
    mod = load(vdir)
    os.makedirs(f"{vdir}/build", exist_ok=True)
    os.makedirs(f"{vdir}/output", exist_ok=True)
    if len(sys.argv) > 3 and sys.argv[2] == "--still":
        for ts in sys.argv[3:]:
            frame(mod, float(ts)).write_to_png(f"{vdir}/build/still_{float(ts):05.2f}.png")
        return
    wav = music.arrange(f"{vdir}/build/audio.wav", cues=mod.cues(), dur=mod.DUR, **mod.MUSIC)
    mp4 = f"{vdir}/build/video.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{fx.W}x{fx.H}",
         "-r", str(fx.FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         mp4], stdin=subprocess.PIPE)
    for f in range(int(round(mod.DUR * fx.FPS))):
        ff.stdin.write(bytes(frame(mod, f / fx.FPS).get_data()))
    ff.stdin.close()
    ff.wait()
    out = f"{vdir}/output/{name}_preview.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    summ = [ln.strip() for ln in r.stderr.splitlines() if ln.strip().startswith(("I:", "Peak:"))]
    print("wrote", out, "|", " ".join(summ[-2:]))


if __name__ == "__main__":
    main()
