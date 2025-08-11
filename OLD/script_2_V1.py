# -*- coding: utf-8 -*-
"""
Construit des pages HTML statiques à partir des manifestes produits par Script 1.

Entrées attendues (par défaut dans ./vocab_audio) :
  - manifest_global.json
  - lessons/_index.json
  - lessons/<lesson_id>.json
  - audio/*.mp3

Sorties :
  - index.html                 (liste des leçons + recherche globale)
  - lesson-<id>.html           (page par leçon)
  - (aucune copie d'audio : on pointe vers vocab_audio/audio/*.mp3)

Usage :
  python build_interface_from_manifests.py
Options :
  --root DIR     (dossier racine des manifestes et audios, défaut: vocab_audio)
  --out  DIR     (dossier de sortie HTML, défaut: <root>)  # garde tout ensemble
  --title "..."  (titre de l'index)
"""

import argparse
import json
from pathlib import Path
from html import escape

# -------------------------
# Utilities
# -------------------------

BASE_CSS = """
:root{
  --bg:#0b0f14;--card:#121821;--text:#eef3fb;--muted:#b8c0cc;--accent:#5aa0ff;--accent2:#8ad1ff;--border:#1e2632
}
*{box-sizing:border-box}
body{
  margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  background:radial-gradient(1000px 600px at 20% -10%,#16202d 0%,#0b0f14 60%) no-repeat fixed,var(--bg);
  color:var(--text);padding:32px 16px 80px
}
.container{max-width:1000px;margin:0 auto}
h1{margin:0 0 8px}
.sub{color:var(--muted);margin:0 0 24px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.card{
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border:1px solid var(--border);border-radius:16px;padding:16px;display:flex;gap:12px;align-items:center
}
.badge{
  min-width:36px;height:36px;border-radius:10px;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--accent),var(--accent2));color:#0b0f14;font-weight:700;
  border:1px solid rgba(255,255,255,.2);box-shadow:0 6px 14px rgba(90,160,255,.35)
}
.texts{flex:1;min-width:0}
.pt{font-size:18px;font-weight:700;line-height:1.2}
.fr{color:var(--muted);margin-top:2px;font-size:14px}
.actions{display:flex;gap:8px;flex-wrap:wrap}
button{
  border:1px solid var(--border);background:#0e141d;color:var(--text);
  border-radius:10px;padding:8px 12px;cursor:pointer;font-weight:600;
  transition:transform .05s ease,border-color .2s ease
}
button:hover{border-color:var(--accent)}
button:active{transform:translateY(1px)}
.footer{
  position:fixed;left:0;right:0;bottom:0;
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border-top:1px solid var(--border);padding:10px 16px;color:var(--muted);font-size:12px;display:flex;justify-content:center
}
.toolbar{display:flex;gap:10px;align-items:center;margin:16px 0 20px;flex-wrap:wrap}
.toolbar input{
  flex:1;min-width:220px;padding:10px 12px;border-radius:10px;border:1px solid var(--border);
  background:#0e141d;color:var(--text);outline:none
}
a.btn{
  text-decoration:none;border:1px solid var(--border);background:#0e141d;color:var(--text);
  border-radius:10px;padding:8px 12px;font-weight:600
}
.small{font-size:12px;color:var(--muted)}
.header-row{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
"""

BASE_JS = """
const player = document.getElementById('player');
function play(src){ player.src = src; player.play(); }
function filterCards(){
  const q=(document.getElementById('search')?.value||'').trim().toLowerCase();
  const cards=document.querySelectorAll('#list .card');
  if(!q){ cards.forEach(c=>c.style.display=''); return; }
  cards.forEach(c=>{
    const pt=c.getAttribute('data-pt'), fr=c.getAttribute('data-fr');
    c.style.display = (pt.includes(q) || fr.includes(q)) ? '' : 'none';
  });
}
function toggleQuiz(){
  const chk=document.getElementById('quiz');
  const frs=document.querySelectorAll('.fr');
  frs.forEach(el=>{ el.style.visibility = chk.checked ? 'hidden' : 'visible'; });
}
"""

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"[ERREUR] Lecture JSON impossible : {path} → {e}")

def build_word_card(idx, pt, fr, file_normal, file_slow=""):
    pt_esc = escape(pt); fr_esc = escape(fr)
    btn_slow = f'<button onclick="play(\'{escape(file_slow)}\')">🐢 Lent</button>' if file_slow else ''
    return f"""
    <div class="card" data-pt="{pt_esc.lower()}" data-fr="{fr_esc.lower()}">
      <div class="badge">{idx}</div>
      <div class="texts">
        <div class="pt">{pt_esc}</div>
        <div class="fr">{fr_esc}</div>
        <div class="small">{escape(file_normal)}</div>
      </div>
      <div class="actions">
        <button onclick="play('{escape(file_normal)}')">▶️ Écouter</button>
        {btn_slow}
      </div>
    </div>
    """

def write_html(out_path: Path, title: str, subtitle: str, body_html: str, show_toolbar=True):
    toolbar = f"""
    <div class="toolbar">
      <input id="search" type="text" placeholder="Rechercher (PT ou FR)..." oninput="filterCards()" />
      <label><input id="quiz" type="checkbox" onchange="toggleQuiz()"> Mode Quiz (cacher FR)</label>
      <span class="small">Astuce : répète à voix haute 3×</span>
    </div>
    """ if show_toolbar else ""
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <title>{escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class="container">
    <div class="header-row">
      <h1>{escape(title)}</h1>
      <a class="btn" href="index.html">🏠 Accueil</a>
    </div>
    <p class="sub">{escape(subtitle)}</p>
    {toolbar}
    {body_html}
  </div>
  <div class="footer">Pages statiques — ouvrez localement sans serveur.</div>
  <audio id="player" preload="auto"></audio>
  <script>{BASE_JS}</script>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")

# -------------------------
# Build pages
# -------------------------

def build_index(root: Path, out_dir: Path, title: str, global_manifest: dict, lessons_index: dict):
    # Stats
    words = global_manifest.get("words", [])
    total_words = len(words)
    total_lessons = len(lessons_index)

    # Liste des leçons
    cards = []
    for lid, lec in lessons_index.items():
        ltitle = lec.get("title", lid)
        count = len(lec.get("words", []))
        cards.append(f"""
        <div class="card">
          <div class="badge">{count}</div>
          <div class="texts">
            <div class="pt">{escape(ltitle)}</div>
            <div class="fr">ID : {escape(lid)}</div>
          </div>
          <div class="actions">
            <a class="btn" href="lesson-{escape(lid)}.html">▶️ Ouvrir la leçon</a>
          </div>
        </div>
        """)

    # Recherche globale (tous les mots)
    all_cards = []
    for i, w in enumerate(words, start=1):
        pt = w.get("pt",""); fr = w.get("fr","")
        files = w.get("files", {})
        all_cards.append(build_word_card(i, pt, fr, files.get("normal",""), files.get("slow","")))

    body = f"""
    <div class="card" style="justify-content:space-between">
      <div>
        <div class="pt">Résumé</div>
        <div class="fr">Leçons : {total_lessons} • Mots uniques : {total_words}</div>
      </div>
      <div class="actions">
        <a class="btn" href="#all">↓ Parcourir tous les mots</a>
      </div>
    </div>

    <h2>Leçons</h2>
    <div class="grid">
      {''.join(cards)}
    </div>

    <h2 id="all">Tous les mots</h2>
    <div class="toolbar">
      <input id="search" type="text" placeholder="Rechercher (PT ou FR)..." oninput="filterCards()" />
      <label><input id="quiz" type="checkbox" onchange="toggleQuiz()"> Mode Quiz (cacher FR)</label>
    </div>
    <div id="list" class="grid">
      {''.join(all_cards)}
    </div>
    """
    write_html(out_dir / "index.html", title, "Sélectionne une leçon ou cherche un mot", body, show_toolbar=False)

def build_lesson_pages(root: Path, out_dir: Path, lessons_index: dict, global_manifest: dict):
    # Map id -> word entry from global manifest
    by_id = {}
    for w in global_manifest.get("words", []):
        wid = w.get("id")
        if wid:
            by_id[wid] = w

    for lid, _ in lessons_index.items():
        path = root / "lessons" / f"{lid}.json"
        lesson = load_json(path)
        title = lesson.get("title", lid)
        words = lesson.get("words", [])

        cards = []
        idx = 1
        missing = []
        for ref in words:
            wid = ref.get("id")
            w = by_id.get(wid)
            if not w:
                missing.append(wid)
                continue
            files = w.get("files", {})
            cards.append(build_word_card(idx, w.get("pt",""), w.get("fr",""), files.get("normal",""), files.get("slow","")))
            idx += 1

        if missing:
            # On affiche un encart d’avertissement en haut de la page
            warn = f"""
            <div class="card">
              <div class="badge">⚠️</div>
              <div class="texts">
                <div class="pt">Références absentes dans le manifeste global</div>
                <div class="fr">{escape(', '.join(missing))}</div>
              </div>
            </div>
            """
        else:
            warn = ""

        body = f"""
        {warn}
        <div id="list" class="grid">
          {''.join(cards)}
        </div>
        """
        write_html(out_dir / f"lesson-{lid}.html", f"Leçon — {title}", f"ID : {lid}", body, show_toolbar=True)

# -------------------------
# Main
# -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default="vocab_audio", help="Racine des manifestes/audios")
    ap.add_argument("--out",  type=str, default="", help="Dossier de sortie HTML (défaut: root)")
    ap.add_argument("--title", type=str, default="Vocabulaire – Portugais brésilien", help="Titre de la page d’accueil")
    args = ap.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out) if args.out else root

    manifest_global_path = root / "manifest_global.json"
    lessons_index_path = root / "lessons" / "_index.json"

    if not manifest_global_path.exists():
        raise SystemExit(f"[ERREUR] introuvable : {manifest_global_path} (as-tu lancé le Script 1 ?)")
    if not lessons_index_path.exists():
        raise SystemExit(f"[ERREUR] introuvable : {lessons_index_path} (as-tu lancé le Script 1 ?)")

    out_dir.mkdir(parents=True, exist_ok=True)

    global_manifest = load_json(manifest_global_path)
    lessons_index = load_json(lessons_index_path)

    # index + pages leçon
    build_index(root, out_dir, args.title, global_manifest, lessons_index)
    build_lesson_pages(root, out_dir, lessons_index, global_manifest)

    print("✅ Interface générée")
    print(f" - Accueil : {out_dir / 'index.html'}")
    print(f" - Leçons  : {out_dir}/lesson-<id>.html")

if __name__ == "__main__":
    main()
