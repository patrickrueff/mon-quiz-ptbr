from html import escape
from pathlib import Path
from utils_write_html import write_html
from utils_build_word_card import build_word_card

def build_index(root: Path, out_dir: Path, title: str, global_manifest: dict, lessons_index: dict):
    words = global_manifest.get("words", [])
    total_words = len(words); total_lessons = len(lessons_index)

    lesson_cards = []
    for lid, lec in lessons_index.items():
        ltitle = lec.get("title", lid)
        count = len(lec.get("words", []))
        lesson_cards.append(f"""        <div class="card">
          <div class="texts">
            <div class="label badge">{count}</div>
            <div>
              <div class="pt">{escape(ltitle)}</div>
              <div class="fr">ID : {escape(lid)}</div>
            </div>
          </div>
          <div class="actions">
            <a class="btn" href="lesson-{escape(lid)}.html">📚 Leçon</a>
            <a class="btn" href="quiz-{escape(lid)}.html">🎧 Quiz</a>
            <a class="btn" href="dictation-{escape(lid)}.html">⌨️ Dictée</a>
          </div>
        </div>
        """)

    all_cards = []
    for i, w in enumerate(words, start=1):
        pt, fr = w.get("pt",""), w.get("fr","")
        phon = w.get("phon","")
        files = w.get("files", {})
        all_cards.append(build_word_card(i, pt, fr, phon, files.get("normal",""), files.get("slow","")))

    body = f"""    <div class="card">
      <div class="texts">
        <div class="label badge">ℹ️</div>
        <div>
          <div class="pt">Résumé</div>
          <div class="fr">Leçons : {total_lessons} • Mots uniques : {total_words}</div>
        </div>
      </div>
      <div class="actions">
        <a class="btn" href="quiz.html">🎧 Quiz global</a>
        <a class="btn" href="dictation.html">⌨️ Dictée globale</a>
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
    write_html(out_dir / "index.html", title, "Navigue dans les leçons, entraîne-toi au quiz ou à la dictée.", body, home_link=False)
