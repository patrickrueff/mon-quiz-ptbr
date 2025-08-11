from pathlib import Path
from utils_write_html import write_html

def build_quiz_page(out_path: Path, title: str, subtitle: str, pool_js_array: str, quiz_js: str, timer_seconds: int):
    body = f"""    <div class="quiz-wrap">
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
          <div class="pill">⏱️ Temps : <span id="timer" class="timer">{timer_seconds}</span>s</div>
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
    extra_js = f"const POOL = {pool_js_array};\n" + quiz_js + "\nstartQuiz(POOL);"
    write_html(out_path, title, subtitle, body, extra_js)
