# -*- coding: utf-8 -*-
"""
Construit l'interface statique (index + pages leçon) ET des pages de Quiz :
 - quiz global : quiz.html
 - quiz par leçon : quiz-<id>.html

Entrées (depuis Script 1) :
  vocab_audio/
    manifest_global.json
    lessons/_index.json
    lessons/<id>.json
    audio/*.mp3

Usage :
  python build_interface_from_manifests.py
  python build_interface_from_manifests.py --root vocab_audio --out vocab_audio --title "Vocabulaire – PT-BR"
"""

import argparse
import json
from pathlib import Path
from html import escape

# ---------- Styles/UI ----------
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
h2{margin:22px 0 12px}
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
button,a.btn{
  border:1px solid var(--border);background:#0e141d;color:var(--text);
  border-radius:10px;padding:8px 12px;cursor:pointer;font-weight:600;
  transition:transform .05s ease,border-color .2s ease;text-decoration:none;display:inline-flex;align-items:center;gap:6px
}
button:hover,a.btn:hover{border-color:var(--accent)}
button:active,a.btn:active{transform:translateY(1px)}
.footer{
  position:fixed;left:0;right:0;bottom:0;
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border-top:1px solid var(--border);padding:10px 16px;color:var(--muted);font-size:12px;display:flex;justify-content:center
}
.toolbar{display:flex;gap:10px;align-items:center;margin:16px 0 20px;flex-wrap:wrap}
.toolbar input,.toolbar select{
  flex:1;min-width:220px;padding:10px 12px;border-radius:10px;border:1px solid var(--border);
  background:#0e141d;color:var(--text);outline:none
}
.header-row{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.small{font-size:12px;color:var(--muted)}
.quiz-wrap{max-width:720px;margin:0 auto}
.quiz-card{
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border:1px solid var(--border);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:14px
}
.choice{
  border:1px solid var(--border);border-radius:10px;padding:10px 12px;cursor:pointer;
  background:#0e141d
}
.choice.correct{border-color:#3ddc97}
.choice.wrong{border-color:#ff6b6b}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.kpi{display:flex;gap:12px}
.kpi .pill{
  padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:#0e141d;color:var(--text)
}
.center{display:flex;justify-content:center}
"""

BASE_JS_COMMON = """
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

# ---------- Helpers ----------
def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

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

def write_html(out_path: Path, title: str, subtitle: str, body_html: str, extra_js: str = "", home_link=True):
    home_btn = '<a class="btn" href="index.html">🏠 Accueil</a>' if home_link else ''
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
      <div class="row">{home_btn}</div>
    </div>
    <p class="sub">{escape(subtitle)}</p>
    {body_html}
  </div>
  <div class="footer">Pages statiques — ouvrez localement sans serveur.</div>
  <audio id="player" preload="auto"></audio>
  <script>{BASE_JS_COMMON}</script>
  <script>{extra_js}</script>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")

# ---------- Pages “catalogue” ----------
def build_index(root: Path, out_dir: Path, title: str, global_manifest: dict, lessons_index: dict):
    words = global_manifest.get("words", [])
    total_words = len(words); total_lessons = len(lessons_index)

    # Cartes leçons
    lesson_cards = []
    for lid, lec in lessons_index.items():
        ltitle = lec.get("title", lid)
        count = len(lec.get("words", []))
        lesson_cards.append(f"""
        <div class="card">
          <div class="badge">{count}</div>
          <div class="texts">
            <div class="pt">{escape(ltitle)}</div>
            <div class="fr">ID : {escape(lid)}</div>
          </div>
          <div class="actions">
            <a class="btn" href="lesson-{escape(lid)}.html">📚 Ouvrir la leçon</a>
            <a class="btn" href="quiz-{escape(lid)}.html">🎧 Quiz</a>
          </div>
        </div>
        """)

    # Tous les mots
    all_cards = []
    for i, w in enumerate(words, start=1):
        pt, fr = w.get("pt",""), w.get("fr","")
        files = w.get("files", {})
        all_cards.append(build_word_card(i, pt, fr, files.get("normal",""), files.get("slow","")))

    body = f"""
    <div class="card" style="justify-content:space-between">
      <div>
        <div class="pt">Résumé</div>
        <div class="fr">Leçons : {total_lessons} • Mots uniques : {total_words}</div>
      </div>
      <div class="actions">
        <a class="btn" href="quiz.html">🎧 Lancer le quiz global</a>
      </div>
    </div>

    <h2>Leçons</h2>
    <div class="grid">{''.join(lesson_cards)}</div>

    <h2 id="all">Tous les mots</h2>
    <div class="toolbar">
      <input id="search" type="text" placeholder="Rechercher (PT ou FR)..." oninput="filterCards()" />
      <label><input id="quiz" type="checkbox" onchange="toggleQuiz()"> Mode Quiz (cacher FR)</label>
    </div>
    <div id="list" class="grid">{''.join(all_cards)}</div>
    """
    write_html(out_dir / "index.html", title, "Navigue dans les leçons ou entraîne-toi au quiz.", body, home_link=False)

def build_lesson_pages(root: Path, out_dir: Path, lessons_index: dict, global_manifest: dict):
    by_id = {w.get("id"): w for w in global_manifest.get("words", []) if w.get("id")}
    for lid, _ in lessons_index.items():
        lesson = load_json(root / "lessons" / f"{lid}.json")
        title = lesson.get("title", lid)
        words = lesson.get("words", [])

        cards = []
        for idx, ref in enumerate(words, start=1):
            w = by_id.get(ref.get("id"))
            if not w: continue
            files = w.get("files", {})
            cards.append(build_word_card(idx, w.get("pt",""), w.get("fr",""), files.get("normal",""), files.get("slow","")))

        body = f"""
        <div class="actions" style="margin-bottom:12px">
          <a class="btn" href="quiz-{escape(lid)}.html">🎧 Quiz de cette leçon</a>
        </div>
        <div class="toolbar">
          <input id="search" type="text" placeholder="Rechercher (PT ou FR)..." oninput="filterCards()" />
          <label><input id="quiz" type="checkbox" onchange="toggleQuiz()"> Mode Quiz (cacher FR)</label>
        </div>
        <div id="list" class="grid">{''.join(cards)}</div>
        """
        write_html(out_dir / f"lesson-{lid}.html", f"Leçon — {title}", f"ID : {lid}", body)

# ---------- Pages “Quiz” ----------
QUIZ_JS = """
function shuffle(a){ for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }

function makeQuiz(POOL, limit){
  // POOL: [{pt, fr, normal, slow?}]
  const items = [...POOL];
  shuffle(items);
  if (limit && limit>0) { items.length = Math.min(limit, items.length); }
  return items;
}

function buildChoices(pool, answer, n=4){
  // n-1 distracteurs + 1 bonne réponse
  const others = pool.filter(x => x.pt !== answer.pt);
  shuffle(others);
  const picks = others.slice(0, Math.max(0, n-1));
  const options = shuffle([...picks, answer]);
  return options;
}

function QuizApp(config){
  const state = {
    pool: config.pool,
    idx: 0,
    score: 0,
    total: config.total,
    optionsCount: config.optionsCount || 4
  };

  const elAudioBtn = document.getElementById('play-audio');
  const elQuestion = document.getElementById('qnum');
  const elScore = document.getElementById('score');
  const elChoices = document.getElementById('choices');
  const elNext = document.getElementById('next');
  const elResult = document.getElementById('result');

  function render(){
    const cur = state.pool[state.idx];
    elQuestion.textContent = (state.idx + 1) + " / " + state.total;
    elScore.textContent = state.score;

    // Audio
    elAudioBtn.onclick = () => { play(cur.normal); };
    // Options
    elChoices.innerHTML = "";
    const opts = buildChoices(state.pool, cur, state.optionsCount);
    opts.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'choice';
      btn.textContent = opt.pt;
      btn.onclick = () => onAnswer(opt.pt === cur.pt, btn);
      elChoices.appendChild(btn);
    });
    elNext.disabled = true;
    elResult.textContent = "";
  }

  function onAnswer(isCorrect, btn){
    // verrouille
    const buttons = elChoices.querySelectorAll('.choice');
    buttons.forEach(b => b.disabled = true);
    // style
    if(isCorrect){
      btn.classList.add('correct');
      state.score += 1;
      elResult.textContent = "✅ Correct !";
    }else{
      btn.classList.add('wrong');
      // surligne la bonne réponse
      buttons.forEach(b => { if(b.textContent === state.pool[state.idx].pt) b.classList.add('correct'); });
      elResult.textContent = "❌ Mauvaise réponse.";
    }
    elScore.textContent = state.score;
    elNext.disabled = false;
  }

  elNext.onclick = () => {
    if (state.idx + 1 >= state.total){
      // fin
      elChoices.innerHTML = "";
      elAudioBtn.disabled = true;
      elNext.disabled = true;
      elResult.textContent = "🎉 Terminé ! Score : " + state.score + " / " + state.total;
      return;
    }
    state.idx += 1;
    render();
  };

  render();
}

function startQuiz(POOL){
  const sel = document.getElementById('qcount');
  const total = parseInt(sel.value, 10) || 10;
  const optionsCount = 4;
  const subset = makeQuiz(POOL, total);
  document.getElementById('config').style.display = 'none';
  document.getElementById('stage').style.display = 'block';
  QuizApp({ pool: subset, total: subset.length, optionsCount });
}
"""

def build_quiz_page(out_path: Path, title: str, subtitle: str, pool_js_array: str):
    body = f"""
    <div class="quiz-wrap">
      <div id="config" class="quiz-card">
        <div class="pt">Paramètres du quiz</div>
        <div class="row">
          <label for="qcount">Nombre de questions</label>
          <select id="qcount">
            <option value="10" selected>10</option>
            <option value="5">5</option>
            <option value="15">15</option>
            <option value="20">20</option>
          </select>
          <button onclick="startQuiz(POOL)">▶️ Démarrer</button>
        </div>
        <div class="small">Le quiz jouera un audio aléatoire. Choisis le bon mot en portugais.</div>
      </div>

      <div id="stage" class="quiz-card" style="display:none">
        <div class="row kpi">
          <div class="pill">Question : <span id="qnum">1</span></div>
          <div class="pill">Score : <span id="score">0</span></div>
        </div>
        <div class="row">
          <button id="play-audio">🔊 Lire l'audio</button>
          <span class="small">Astuce : réécoute avant de répondre.</span>
        </div>
        <div id="choices" class="grid" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr));"></div>
        <div class="row">
          <button id="next" disabled>Question suivante</button>
          <span id="result"></span>
        </div>
      </div>
    </div>
    """
    extra_js = f"const POOL = {pool_js_array};\n" + QUIZ_JS
    write_html(out_path, title, subtitle, body, extra_js)

def to_quiz_pool_js(words_list):
    """
    Convertit la liste de mots (manifest_global 'words' filtrés) en tableau JS :
      [{pt:'...', fr:'...', normal:'audio/xxx.mp3', slow:'audio/xxx-slow.mp3'?}, ...]
    On garde seulement les entrées avec un fichier 'normal'.
    """
    arr = []
    for w in words_list:
        files = w.get("files", {})
        normal = files.get("normal")
        if not normal: continue
        obj = {
            "pt": w.get("pt",""),
            "fr": w.get("fr",""),
            "normal": normal
        }
        if "slow" in files:
            obj["slow"] = files["slow"]
        arr.append(obj)
    # JSON sécurisé
    return json.dumps(arr, ensure_ascii=False)

def build_quiz_pages(root: Path, out_dir: Path, lessons_index: dict, global_manifest: dict):
    # Quiz global
    all_words = global_manifest.get("words", [])
    pool_js = to_quiz_pool_js(all_words)
    build_quiz_page(out_dir / "quiz.html", "Quiz — Tous les mots", "Clique sur la bonne réponse après écoute.", pool_js)

    # Quiz par leçon
    by_id = {w.get("id"): w for w in all_words if w.get("id")}
    for lid, _ in lessons_index.items():
        lesson = load_json(root / "lessons" / f"{lid}.json")
        title = lesson.get("title", lid)
        words = []
        for ref in lesson.get("words", []):
            w = by_id.get(ref.get("id"))
            if w: words.append(w)
        pool_js = to_quiz_pool_js(words)
        build_quiz_page(out_dir / f"quiz-{lid}.html", f"Quiz — {title}", f"Leçon : {lid}", pool_js)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default="vocab_audio", help="Racine des manifestes/audios")
    ap.add_argument("--out",  type=str, default="", help="Dossier de sortie HTML (défaut: root)")
    ap.add_argument("--title", type=str, default="Vocabulaire – Portugais brésilien", help="Titre de l’index")
    args = ap.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out) if args.out else root
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_global_path = root / "manifest_global.json"
    lessons_index_path = root / "lessons" / "_index.json"
    if not manifest_global_path.exists():
        raise SystemExit(f"[ERREUR] introuvable : {manifest_global_path}")
    if not lessons_index_path.exists():
        raise SystemExit(f"[ERREUR] introuvable : {lessons_index_path}")

    global_manifest = load_json(manifest_global_path)
    lessons_index = load_json(lessons_index_path)

    # Pages catalogue
    build_index(root, out_dir, args.title, global_manifest, lessons_index)
    build_lesson_pages(root, out_dir, lessons_index, global_manifest)

    # Pages quiz
    build_quiz_pages(root, out_dir, lessons_index, global_manifest)

    print("✅ Interface + Quiz générés")
    print(f" - Accueil : {out_dir / 'index.html'}")
    print(f" - Quiz global : {out_dir / 'quiz.html'}")
    print(f" - Quiz leçon : {out_dir}/quiz-<id>.html")

if __name__ == "__main__":
    main()
