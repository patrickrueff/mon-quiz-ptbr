# -*- coding: utf-8 -*-
"""
Interface statique (index + leçons) + Quiz audio auto + compte à rebours.
MAJ :
 - Affiche la phonétique 'phon' si présente (dans manifest_global)
 - Ne montre plus le nom/chemin du fichier audio dans les cartes
"""

import argparse, json
from pathlib import Path
from html import escape

# ---------- Styles/UI ----------
BASE_CSS = """
:root{
  --bg:#0b0f14;--card:#121821;--text:#eef3fb;--muted:#b8c0cc;--accent:#5aa0ff;--accent2:#8ad1ff;--border:#1e2632
}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  background:radial-gradient(1000px 600px at 20% -10%,#16202d 0%,#0b0f14 60%) no-repeat fixed,var(--bg);
  color:var(--text);padding:32px 16px 80px}
.container{max-width:1000px;margin:0 auto}
h1{margin:0 0 8px} h2{margin:22px 0 12px} .sub{color:var(--muted);margin:0 0 24px}
.card{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border:1px solid var(--border);border-radius:16px;padding:16px;display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center}
.badge{min-width:36px;height:36px;border-radius:10px;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--accent),var(--accent2));color:#0b0f14;font-weight:700;border:1px solid rgba(255,255,255,.2);
  box-shadow:0 6px 14px rgba(90,160,255,.35)}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.texts{display:flex;gap:12px;align-items:center}
.texts .label{display:grid;place-items:center}
.pt{font-size:18px;font-weight:700;line-height:1.2}
.phon{color:#9fb4cc;font-size:13px;margin-top:2px}
.fr{color:var(--muted);margin-top:2px;font-size:14px}
.actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
button,a.btn{border:1px solid var(--border);background:#0e141d;color:#eef3fb;border-radius:10px;padding:8px 12px;cursor:pointer;font-weight:600;
  transition:transform .05s ease,border-color .2s ease;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
button:hover,a.btn:hover{border-color:var(--accent)} button:active,a.btn:active{transform:translateY(1px)}
.small{font-size:12px;color:var(--muted)}
.footer{position:fixed;left:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border-top:1px solid var(--border);padding:10px 16px;color:var(--muted);font-size:12px;display:flex;justify-content:center}
.toolbar{display:flex;gap:10px;align-items:center;margin:16px 0 20px;flex-wrap:wrap}
.toolbar input,.toolbar select{flex:1;min-width:220px;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:#0e141d;color:#eef3fb;outline:none}
.quiz-wrap{max-width:720px;margin:0 auto}
.quiz-card{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:14px}
.choice{border:1px solid var(--border);border-radius:10px;padding:10px 12px;cursor:pointer;background:#0e141d}
.choice.correct{border-color:#3ddc97} .choice.wrong{border-color:#ff6b6b}
.kpi{display:flex;gap:12px;flex-wrap:wrap}
.kpi .pill{padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:#0e141d;color:#eef3fb}
.timer{font-weight:700}
@media (max-width:640px){.card{grid-template-columns:1fr}.actions{justify-content:flex-start}}
"""

BASE_JS_COMMON = """
const player = document.getElementById('player');
function play(src){ player.src = src; player.play(); }
function stopAudio(){ try{ player.pause(); player.currentTime = 0; }catch(e){} }
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

def build_word_card(idx, pt, fr, phon, file_normal, file_slow=""):
    pt_esc, fr_esc = escape(pt), escape(fr)
    phon_esc = escape(phon) if phon else ""
    btn_slow = f'<button onclick="play(\'{escape(file_slow)}\')">🐢 Lent</button>' if file_slow else ''
    return f"""
    <div class="card" data-pt="{pt_esc.lower()}" data-fr="{fr_esc.lower()}">
      <div class="texts">
        <div class="label badge">{idx}</div>
        <div>
          <div class="pt">{pt_esc}</div>
          {f'<div class="phon">[{phon_esc}]</div>' if phon_esc else ''}
          <div class="fr">{fr_esc}</div>
        </div>
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
    <div class="row" style="justify-content:space-between;align-items:baseline">
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

# ---------- Pages catalogue ----------
def build_index(root: Path, out_dir: Path, title: str, global_manifest: dict, lessons_index: dict):
    words = global_manifest.get("words", [])
    total_words = len(words); total_lessons = len(lessons_index)

    lesson_cards = []
    for lid, lec in lessons_index.items():
        ltitle = lec.get("title", lid)
        count = len(lec.get("words", []))
        lesson_cards.append(f"""
        <div class="card">
          <div class="texts">
            <div class="label badge">{count}</div>
            <div>
              <div class="pt">{escape(ltitle)}</div>
              <div class="fr">ID : {escape(lid)}</div>
            </div>
          </div>
          <div class="actions">
            <a class="btn" href="lesson-{escape(lid)}.html">📚 Ouvrir la leçon</a>
            <a class="btn" href="quiz-{escape(lid)}.html">🎧 Quiz</a>
          </div>
        </div>
        """)

    all_cards = []
    for i, w in enumerate(words, start=1):
        pt, fr = w.get("pt",""), w.get("fr","")
        phon = w.get("phon","")
        files = w.get("files", {})
        all_cards.append(build_word_card(i, pt, fr, phon, files.get("normal",""), files.get("slow","")))

    body = f"""
    <div class="card">
      <div class="texts">
        <div class="label badge">ℹ️</div>
        <div>
          <div class="pt">Résumé</div>
          <div class="fr">Leçons : {total_lessons} • Mots uniques : {total_words}</div>
        </div>
      </div>
      <div class="actions">
        <a class="btn" href="quiz.html">🎧 Quiz global</a>
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
            cards.append(build_word_card(
                idx,
                w.get("pt",""), w.get("fr",""), w.get("phon",""),
                files.get("normal",""), files.get("slow","")
            ))

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

# ---------- Quiz (auto-next + pause + timer) ----------
QUIZ_JS = r"""
function shuffle(a){ for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
function makeQuiz(POOL, limit){ const items=[...POOL]; shuffle(items); if(limit&&limit>0){ items.length=Math.min(limit,items.length);} return items; }
function buildChoices(pool, answer, n=4){
  const others = pool.filter(x => x.pt !== answer.pt);
  shuffle(others);
  const picks = others.slice(0, Math.max(0, n-1));
  return shuffle([...picks, answer]);
}
function QuizApp(config){
  const AUTO_DELAY_MS = 900;
  const TIMER_LIMIT_S = 8;
  const state = { pool:config.pool, idx:0, score:0, total:config.total, optionsCount:4,
                  started:false, paused:false, timerNext:null, countdown:TIMER_LIMIT_S,
                  countdownInterval:null, answered:false };
  const elBtnStart   = document.getElementById('btn-start');
  const elBtnPause   = document.getElementById('btn-pause');
  const elBtnResume  = document.getElementById('btn-resume');
  const elBtnRestart = document.getElementById('btn-restart');
  const elQuestion = document.getElementById('qnum');
  const elScore    = document.getElementById('score');
  const elTimer    = document.getElementById('timer');
  const elChoices  = document.getElementById('choices');
  const elResult   = document.getElementById('result');
  const elConfig   = document.getElementById('config');
  const elStage    = document.getElementById('stage');

  function setButtons(){
    elBtnStart.style.display   = state.started ? 'none' : 'inline-flex';
    elBtnPause.style.display   = (state.started && !state.paused) ? 'inline-flex' : 'none';
    elBtnResume.style.display  = (state.started && state.paused) ? 'inline-flex' : 'none';
    elBtnRestart.style.display = state.started ? 'inline-flex' : 'none';
  }
  function clearTimers(){
    if (state.timerNext){ clearTimeout(state.timerNext); state.timerNext = null; }
    if (state.countdownInterval){ clearInterval(state.countdownInterval); state.countdownInterval = null; }
  }
  function scheduleNext(){ if(state.paused) return; if(state.timerNext){clearTimeout(state.timerNext);} state.timerNext=setTimeout(nextQuestion,AUTO_DELAY_MS); }
  function startCountdown(){
    if (state.countdownInterval){ clearInterval(state.countdownInterval); }
    state.countdown = TIMER_LIMIT_S;
    elTimer.textContent = state.countdown.toString();
    state.countdownInterval = setInterval(() => {
      if (state.paused) return;
      state.countdown -= 1;
      elTimer.textContent = Math.max(0, state.countdown).toString();
      if (state.countdown <= 0){
        clearInterval(state.countdownInterval);
        onTimeout();
      }
    }, 1000);
  }
  function stopCountdown(){ if(state.countdownInterval){ clearInterval(state.countdownInterval); state.countdownInterval=null; } }
  function render(){
    const cur = state.pool[state.idx];
    state.answered = false;
    elQuestion.textContent = (state.idx + 1) + " / " + state.total;
    elScore.textContent = state.score;
    elResult.textContent = "";
    elChoices.innerHTML = "";
    const opts = buildChoices(state.pool, cur, state.optionsCount);
    opts.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'choice';
      btn.textContent = opt.pt;
      btn.onclick = () => onAnswer(opt.pt === cur.pt, btn);
      elChoices.appendChild(btn);
    });
    if (!state.paused) {
      stopAudio();
      play(cur.normal);
      startCountdown();
    }
  }
  function lockChoices(){ elChoices.querySelectorAll('.choice').forEach(b => b.disabled = true); }
  function markCorrect(){
    elChoices.querySelectorAll('.choice').forEach(b => {
      if (b.textContent === state.pool[state.idx].pt) b.classList.add('correct');
    });
  }
  function onAnswer(isCorrect, btn){
    if (state.answered) return;
    state.answered = true;
    stopCountdown();
    lockChoices();
    if (isCorrect){ btn.classList.add('correct'); state.score += 1; elResult.textContent = "✅ Correct !"; }
    else { btn.classList.add('wrong'); markCorrect(); elResult.textContent = "❌ Mauvaise réponse."; }
    elScore.textContent = state.score;
    scheduleNext();
  }
  function onTimeout(){
    if (state.answered) return;
    state.answered = true;
    lockChoices(); markCorrect();
    elResult.textContent = "⏰ Temps écoulé.";
    scheduleNext();
  }
  function nextQuestion(){
    clearTimers();
    if (state.idx + 1 >= state.total){
      elChoices.innerHTML = "";
      elResult.textContent = "🎉 Terminé ! Score : " + state.score + " / " + state.total;
      setButtons();
      return;
    }
    state.idx += 1; render();
  }

  // Contrôles
  elBtnStart.onclick = () => {
    const sel = document.getElementById('qcount');
    const total = parseInt(sel.value, 10) || 10;
    state.pool = makeQuiz(state.pool, total);
    state.total = state.pool.length;
    state.idx = 0; state.score = 0; state.started = true; state.paused = false;
    clearTimers(); stopAudio(); elConfig.style.display = 'none'; elStage.style.display = 'block';
    render(); setButtons();
  };
  elBtnPause.onclick = () => { state.paused = True = true; clearTimers(); stopAudio(); setButtons(); };
  elBtnResume.onclick = () => { state.paused = false; setButtons(); render(); };
  elBtnRestart.onclick = () => { clearTimers(); state.started=false; state.paused=false; state.idx=0; state.score=0; stopAudio(); elStage.style.display='none'; elConfig.style.display='block'; setButtons(); };
  setButtons();
}
function startQuiz(POOL){ QuizApp({ pool: POOL, total: POOL.length }); }
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
          <button id="btn-start">▶️ Démarrer</button>
        </div>
        <div class="small">Le quiz joue automatiquement l’audio. Réponds avant la fin du <b>compte à rebours</b>.</div>
      </div>

      <div id="stage" class="quiz-card" style="display:none">
        <div class="row kpi">
          <div class="pill">Question : <span id="qnum">1</span></div>
          <div class="pill">Score : <span id="score">0</span></div>
          <div class="pill">⏱️ Temps : <span id="timer" class="timer">8</span>s</div>
        </div>
        <div id="choices" class="grid" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr));"></div>
        <div class="row" style="gap:8px">
          <button id="btn-pause" style="display:none">⏸️ Pause</button>
          <button id="btn-resume" style="display:none">▶️ Reprendre</button>
          <button id="btn-restart" style="display:none">🔄 Recommencer</button>
          <span id="result"></span>
        </div>
      </div>
    </div>
    """
    extra_js = f"const POOL = {pool_js_array};\n" + QUIZ_JS + "\nstartQuiz(POOL);"
    write_html(out_path, title, subtitle, body, extra_js)

def to_quiz_pool_js(words_list):
    arr = []
    for w in words_list:
        files = w.get("files", {})
        normal = files.get("normal")
        if not normal: continue
        arr.append({"pt": w.get("pt",""), "fr": w.get("fr",""), "normal": normal})
    return json.dumps(arr, ensure_ascii=False)

def build_quiz_pages(root: Path, out_dir: Path, lessons_index: dict, global_manifest: dict):
    all_words = global_manifest.get("words", [])
    pool_js = to_quiz_pool_js(all_words)
    build_quiz_page(out_dir / "quiz.html", "Quiz — Tous les mots", "Clique sur la bonne réponse après écoute.", pool_js)

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
    ap.add_argument("--root", type=str, default="vocab_audio")
    ap.add_argument("--out",  type=str, default="")
    ap.add_argument("--title", type=str, default="Vocabulaire – Portugais brésilien")
    args = ap.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out) if args.out else root
    out_dir.mkdir(parents=True, exist_ok=True)

    mg = root / "manifest_global.json"
    li = root / "lessons" / "_index.json"
    if not mg.exists(): raise SystemExit(f"[ERREUR] {mg} introuvable")
    if not li.exists(): raise SystemExit(f"[ERREUR] {li} introuvable")

    global_manifest = load_json(mg)
    lessons_index   = load_json(li)

    build_index(root, out_dir, args.title, global_manifest, lessons_index)
    build_lesson_pages(root, out_dir, lessons_index, global_manifest)
    build_quiz_pages(root, out_dir, lessons_index, global_manifest)

    print("✅ Interface + Quiz générés")
    print(f" - Accueil : {out_dir / 'index.html'}")
    print(f" - Quiz global : {out_dir / 'quiz.html'}")
    print(f" - Quiz leçon : {out_dir}/quiz-<id>.html")

if __name__ == "__main__":
    main()
