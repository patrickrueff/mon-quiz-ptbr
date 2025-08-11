# 14_pages_build_dictation_page.py
from pathlib import Path
from utils_write_html import write_html

def build_dictation_page(out_path: Path, title: str, subtitle: str, pool_js_array: str, dictation_js: str, timer_seconds: int):
    body = f"""    <div class="quiz-wrap">
      <div id="config" class="quiz-card">
        <div class="pt">Paramètres dictée</div>
        <div class="row">
          <button id="btn-start">▶️ Démarrer</button>
        </div>
        <div class="small">Écoute l’audio puis <b>saisis exactement</b> ce que tu entends.</div>
      </div>

      <div id="stage" class="quiz-card" style="display:none">
        <div class="row kpi">
          <div class="pill">Question : <span id="qnum">1</span></div>
          <div class="pill">Score : <span id="score">0</span></div>
          <div class="pill">⏱️ Temps : <span id="timer" class="timer">{timer_seconds}</span>s</div>
        </div>
        <input id="answer" type="text" placeholder="Tape ici..." style="padding:10px;border-radius:10px;border:1px solid var(--border);background:#0e141d;color:#eef3fb;outline:none" />
        <div class="row" style="gap:8px">
          <button id="btn-check">✔️ Vérifier</button>
          <button id="btn-next" style="display:none">➡️ Suivant</button>
          <button id="btn-restart" style="display:none">🔄 Recommencer</button>
          <span id="result"></span>
        </div>
      </div>
    </div>
    """
    extra_js = f"const POOL = {pool_js_array};\n" + dictation_js + "\nstartDictationQuiz(POOL);"
    write_html(out_path, title, subtitle, body, extra_js)
