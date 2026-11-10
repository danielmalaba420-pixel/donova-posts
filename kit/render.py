#!/usr/bin/env python3
"""Rendu des slides Instagram Donova (1080x1350, JPEG).

Usage :  python3 kit/render.py <dossier_du_post>
Le dossier doit contenir post.json (voir kit/exemple-post.json) et, si besoin,
les photos citées dans le JSON (chemins relatifs au dossier du post).
Produit slide-1.jpg, slide-2.jpg, ... dans ce même dossier.

Types de slides :
  cover   : grande photo en haut + titre + "swipe"         (photo, tag, title, photo_credit)
  text    : tag + gros chiffre/mot optionnel + titre + texte (tag, big, title, body)
  split   : photo à droite + titre + texte à gauche          (photo, tag, title, body, photo_credit)
  tips    : liste numérotée de conseils (3 à 5)               (tag, title, tips:[{t,d}])
  cta     : leçon + 3 puces + encadré rouge d'appel à l'action (tag, title, bullets, cta_title, cta_text)
  chat    : fausse conversation (bulles) pour l'humour         (tag, who, status, messages:[{from:'them'|'me', text, time}], note)
  versus  : deux cartes « ce qu'il dit / ce qu'il veut dire »    (tag, title, a:{label,text}, b:{label,text}, note)
Dans title/body, entourer un mot de *astérisques* le met en rouge (title) ou en gras (body).
"""
import json, re, sys, html, pathlib
from playwright.sync_api import sync_playwright

KIT = pathlib.Path(__file__).resolve().parent
LOGO = (KIT / "logo.svg").as_uri()

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#0d0d0f;font-family:'Poppins',sans-serif;color:#fff;position:relative;overflow:hidden}
.tag{display:inline-block;background:#e10600;font-weight:700;font-size:22px;letter-spacing:3px;padding:10px 20px;border-radius:6px;text-transform:uppercase}
.cnt{position:absolute;top:84px;right:84px;font-family:'Inter';font-size:24px;color:#cfcfd4;background:rgba(0,0,0,.45);padding:8px 16px;border-radius:30px;z-index:5}
h1{font-weight:800;letter-spacing:-2px;line-height:1.04}
h1 em{font-style:normal;color:#e10600}
.p{font-family:'Inter';font-size:32px;line-height:1.5;color:#cfcfd4}
.p strong{color:#fff}
.foot{position:absolute;left:84px;right:84px;bottom:56px;display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(255,255,255,.15);padding-top:26px;z-index:5}
.logo{display:flex;align-items:center;gap:14px}
.word{font-weight:800;font-size:30px;letter-spacing:4px}
.handle{font-family:'Inter';font-size:21px;color:#b9b9c0;text-align:right}
.credit{position:absolute;font-family:'Inter';font-size:16px;color:rgba(255,255,255,.6);z-index:5}
.glowTR{position:absolute;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(225,6,0,.30),transparent 65%);top:-380px;right:-320px}
.glowBL{position:absolute;width:1000px;height:1000px;border-radius:50%;background:radial-gradient(circle,rgba(225,6,0,.35),transparent 65%);bottom:-480px;left:-360px}
.tip{display:flex;gap:26px;align-items:flex-start;background:#17171b;border:1px solid #26262c;border-radius:18px;padding:22px 28px}
.tip .n{font-size:44px;font-weight:800;color:#e10600;min-width:58px;line-height:1}
.tip b{display:block;font-size:30px;font-weight:700;line-height:1.15}
.bub{max-width:760px;padding:20px 26px;border-radius:26px;font-family:'Inter';font-size:32px;line-height:1.35;position:relative}
.bub.them{background:#1f1f25;color:#fff;border-bottom-left-radius:6px;align-self:flex-start}
.bub.me{background:#e10600;color:#fff;border-bottom-right-radius:6px;align-self:flex-end}
.bub small{display:block;font-size:19px;opacity:.6;margin-top:6px;text-align:right}
.vcard{border-radius:24px;padding:36px 40px}
.vcard .lab{font-weight:700;font-size:22px;letter-spacing:3px;text-transform:uppercase;margin-bottom:14px}
.vcard .txt{font-weight:800;font-size:50px;line-height:1.12;letter-spacing:-1px}
.tip p{font-family:'Inter';font-size:22px;color:#a9a9b2;margin-top:6px;line-height:1.35}
"""

def fr(s):
    """Espaces insécables françaises + échappement HTML."""
    s = html.escape(s or "")
    s = s.replace("« ", "«&nbsp;").replace(" »", "&nbsp;»")
    for p in [" :", " ?", " !", " ;"]:
        s = s.replace(p, "&nbsp;" + p[1])
    return s.replace("\n", "<br>")

def title(s):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", fr(s))

def body(s):
    return re.sub(r"\*(.+?)\*", r"<strong>\1</strong>", fr(s))

def foot():
    return (f'<div class="foot"><div class="logo"><img src="{LOGO}" style="width:58px;height:58px">'
            '<div class="word">DONOVA</div></div><div class="handle">@donova.420 · Kinshasa</div></div>')

def slide_html(s, i, n, base):
    k = s["type"]
    cnt = f'<div class="cnt">{i} / {n}</div>'
    tag = f'<span class="tag">{fr(s.get("tag",""))}</span>' if s.get("tag") else ""
    if k == "cover":
        ph = (base / s["photo"]).as_uri()
        out = (f'<img src="{ph}" style="position:absolute;top:0;left:0;width:1080px;height:760px;object-fit:cover;object-position:{s.get("photo_pos","center 55%")}">'
               '<div style="position:absolute;top:0;left:0;width:1080px;height:760px;background:linear-gradient(180deg,rgba(13,13,15,.25) 0%,rgba(13,13,15,0) 40%,#0d0d0f 100%)"></div>'
               + (f'<div class="credit" style="top:720px;right:84px">{fr(s["photo_credit"])}</div>' if s.get("photo_credit") else "")
               + f'<div style="position:absolute;top:84px;left:84px;z-index:5">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;right:84px;top:740px"><h1 style="font-size:{s.get("size",96)}px">{title(s["title"])}</h1>'
               f'<div style="margin-top:40px;font-family:Inter;font-weight:600;font-size:26px">{fr(s.get("swipe","Swipe pour la suite"))} <span style="color:#e10600;font-size:40px">→</span></div></div>')
    elif k == "text":
        big = f'<div style="font-size:{s.get("big_size",190)}px;font-weight:800;color:#e10600;line-height:.95;letter-spacing:-6px;margin-bottom:30px">{fr(s["big"])}</div>' if s.get("big") else ""
        out = (f'<div class="glowTR"></div><div style="position:absolute;top:84px;left:84px">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;right:84px;top:{s.get("top",250)}px">{big}'
               f'<h1 style="font-size:{s.get("size",58)}px">{title(s["title"])}</h1>'
               f'<div class="p" style="margin-top:40px">{body(s.get("body",""))}</div></div>')
    elif k == "split":
        ph = (base / s["photo"]).as_uri()
        out = (f'<img src="{ph}" style="position:absolute;top:0;right:0;width:540px;height:1350px;object-fit:cover;object-position:{s.get("photo_pos","center")}">'
               '<div style="position:absolute;top:0;right:0;width:540px;height:1350px;background:linear-gradient(90deg,#0d0d0f 0%,rgba(13,13,15,.2) 45%,rgba(13,13,15,0) 100%)"></div>'
               + (f'<div class="credit" style="bottom:150px;right:40px">{fr(s["photo_credit"])}</div>' if s.get("photo_credit") else "")
               + f'<div style="position:absolute;top:84px;left:84px;z-index:5">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;width:560px;top:{s.get("top",300)}px;z-index:5">'
               f'<h1 style="font-size:{s.get("size",66)}px">{title(s["title"])}</h1>'
               f'<div class="p" style="margin-top:40px">{body(s.get("body",""))}</div></div>')
    elif k == "tips":
        tips = "".join(f'<div class="tip"><div class="n">{j+1:02d}</div><div><b>{fr(t["t"])}</b><p>{fr(t["d"])}</p></div></div>'
                       for j, t in enumerate(s["tips"]))
        out = (f'<div class="glowTR"></div><div style="position:absolute;top:84px;left:84px">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;right:84px;top:190px"><h1 style="font-size:{s.get("size",64)}px">{title(s["title"])}</h1>'
               f'<div style="margin-top:44px;display:flex;flex-direction:column;gap:20px">{tips}</div></div>')
    elif k == "cta":
        bl = "".join(f'<div class="p">✔︎ &nbsp;{body(b)}</div>' for b in s.get("bullets", []))
        out = (f'<div class="glowBL"></div><div style="position:absolute;top:84px;left:84px">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;right:84px;top:{s.get("top",250)}px">'
               f'<h1 style="font-size:{s.get("size",74)}px">{title(s["title"])}</h1>'
               f'<div style="margin-top:52px;display:flex;flex-direction:column;gap:22px">{bl}</div>'
               f'<div style="margin-top:60px;background:#e10600;border-radius:18px;padding:30px 36px">'
               f'<div style="font-size:34px;font-weight:700">{fr(s.get("cta_title","Ta marque mérite d’être vue."))}</div>'
               f'<div style="font-family:Inter;font-size:26px;margin-top:8px">{fr(s.get("cta_text","Logo, design, pubs, réseaux sociaux : écris-nous en DM 📩"))}</div></div></div>')
    elif k == "chat":
        av = (s.get("who", "Client") or "C")[0].upper()
        msgs = "".join(
            f'<div class="bub {"me" if m.get("from") == "me" else "them"}">{body(m["text"])}'
            + (f'<small>{fr(m["time"])}</small>' if m.get("time") else "") + '</div>'
            for m in s["messages"])
        note = (f'<div class="p" style="margin-top:34px;font-size:30px;text-align:center">{body(s["note"])}</div>' if s.get("note") else "")
        out = (f'<div class="glowTR"></div><div style="position:absolute;top:84px;left:84px">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;right:84px;top:190px">'
               f'<div style="display:flex;align-items:center;gap:20px;background:#17171b;border:1px solid #26262c;border-radius:22px;padding:18px 26px">'
               f'<div style="width:70px;height:70px;border-radius:50%;background:#e10600;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:34px">{html.escape(av)}</div>'
               f'<div><div style="font-weight:700;font-size:32px">{fr(s.get("who","Client"))}</div>'
               f'<div style="font-family:Inter;font-size:22px;color:#7ee081">● {fr(s.get("status","en ligne"))}</div></div></div>'
               f'<div style="margin-top:34px;display:flex;flex-direction:column;gap:18px">{msgs}</div>{note}</div>')
    elif k == "versus":
        a, b = s["a"], s["b"]
        note = (f'<div class="p" style="margin-top:36px;font-size:30px;text-align:center">{body(s["note"])}</div>' if s.get("note") else "")
        out = (f'<div class="glowTR"></div><div style="position:absolute;top:84px;left:84px">{tag}</div>{cnt}'
               f'<div style="position:absolute;left:84px;right:84px;top:{s.get("top",200)}px">'
               + (f'<h1 style="font-size:{s.get("size",56)}px;margin-bottom:40px">{title(s["title"])}</h1>' if s.get("title") else "")
               + f'<div class="vcard" style="background:#17171b;border:1px solid #2a2a31"><div class="lab" style="color:#a9a9b2">{fr(a["label"])}</div><div class="txt">{body(a["text"])}</div></div>'
               f'<div style="text-align:center;font-weight:800;font-size:40px;color:#e10600;margin:22px 0">VS</div>'
               f'<div class="vcard" style="background:#e10600"><div class="lab" style="color:#ffd3d0">{fr(b["label"])}</div><div class="txt">{body(b["text"])}</div></div>{note}</div>')
    else:
        raise SystemExit(f"type de slide inconnu : {k}")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{out}{foot()}</body></html>'

def main():
    base = pathlib.Path(sys.argv[1]).resolve()
    spec = json.loads((base / "post.json").read_text(encoding="utf-8"))
    slides = spec["slides"]
    if len(slides) < 3:
        raise SystemExit("minimum 3 slides par post")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            tmp = base / f".slide-{i}.html"
            tmp.write_text(slide_html(s, i, len(slides), base), encoding="utf-8")
            pg.goto(tmp.as_uri()); pg.wait_for_timeout(600)
            png = base / f".slide-{i}.png"
            pg.screenshot(path=str(png))
            tmp.unlink()
            from PIL import Image
            Image.open(png).convert("RGB").save(base / f"slide-{i}.jpg", quality=90)
            png.unlink()
            print("ok", base / f"slide-{i}.jpg")
        b.close()

if __name__ == "__main__":
    main()
