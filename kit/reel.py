#!/usr/bin/env python3
"""Fabrique un Reel 9:16 (1080x1920, MP4) à partir des slides d'un post déjà rendu.

Usage :  python3 kit/reel.py <dossier_du_post> [--hook "Texte d'accroche"] [--sec 3.0]
Lit slide-1.jpg, slide-2.jpg, ... dans le dossier et écrit reel.mp4.

Mise en page : accroche en haut (reste affichée pendant toute la vidéo), slide au centre
avec léger zoom, barre de progression rouge, « Suis @donova.420 » en bas.
Transitions : glissement latéral. Le Reel est MUET (la musique d'Instagram ne peut pas
être ajoutée par l'API) : le texte doit se suffire à lui-même.
Accroche par défaut : titre de la 1re slide (dans post.json) sans les astérisques.
"""
import argparse, json, pathlib, re, subprocess, sys, textwrap

FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FPS = 30
XF = 0.35  # durée de la transition

def default_hook(base):
    try:
        spec = json.loads((base / "post.json").read_text(encoding="utf-8"))
        for s in spec["slides"]:
            if s.get("title"):
                t = re.sub(r"\*", "", s["title"]).replace("\n", " ")
                return re.sub(r"\s+", " ", t).strip()
    except Exception:
        pass
    return "Donova"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--hook")
    ap.add_argument("--sec", type=float, default=3.0, help="durée d'une slide en secondes")
    a = ap.parse_args()
    base = pathlib.Path(a.dossier).resolve()
    slides = sorted(base.glob("slide-*.jpg"), key=lambda p: int(re.findall(r"\d+", p.stem)[0]))
    if len(slides) < 3:
        sys.exit("il faut au moins 3 slides (slide-N.jpg) dans le dossier")
    n = len(slides)
    d = a.sec + XF                     # durée de chaque clip (avec recouvrement)
    total = round(n * a.sec + XF, 2)

    hook = a.hook or default_hook(base)
    hook = re.sub(r"[\U00010000-\U0010ffff☀-➿]", "", hook).strip()   # pas d'emoji dans drawtext
    lines = textwrap.wrap(hook, 22)[:3]
    (base / ".hook.txt").write_text("\n".join(lines), encoding="utf-8")
    (base / ".foot.txt").write_text("Suis @donova.420", encoding="utf-8")

    inputs, fc = [], []
    for i, s in enumerate(slides):
        inputs += ["-i", str(s)]
        fc.append(f"[{i}:v]scale=1080:1350,pad=1080:1920:0:285:color=0x0d0d0f,setsar=1,"
                  f"zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={int(d*FPS)}:s=1080x1920:fps={FPS}[v{i}]")
    prev = "v0"
    for i in range(1, n):
        off = round(i * a.sec, 2)
        fc.append(f"[{prev}][v{i}]xfade=transition=slideleft:duration={XF}:offset={off}[x{i}]")
        prev = f"x{i}"
    # progression + textes
    fc.append(f"color=c=0xe10600:s=1080x10:r={FPS}:d={total}[bar]")
    fc.append(f"[{prev}][bar]overlay=x='-1080+1080*t/{total}':y=1910[vb]")
    fc.append(f"[vb]drawtext=fontfile={FONT}:textfile={base}/.hook.txt:fontcolor=white:fontsize=60:"
              f"line_spacing=10:x=(w-text_w)/2:y=(285-text_h)/2+10,"
              f"drawtext=fontfile={FONT}:textfile={base}/.foot.txt:fontcolor=0xe10600:fontsize=52:"
              f"x=(w-text_w)/2:y=1635+(285-text_h)/2-20,format=yuv420p[vout]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs,
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n}:a", "-t", str(total),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-r", str(FPS), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(base / "reel.mp4")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    for f in (".hook.txt", ".foot.txt"):
        (base / f).unlink(missing_ok=True)
    if r.returncode:
        sys.exit(r.stderr[-800:])
    print("ok", base / "reel.mp4", f"({total}s)")

if __name__ == "__main__":
    main()
