from pathlib import Path
from utils_write_html import write_html
from utils_build_word_card import build_word_card
from utils_load_json import load_json

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
                idx, w.get("pt",""), w.get("fr",""), w.get("phon",""),
                files.get("normal",""), files.get("slow","")
            ))

        body = f"""        <div class="actions" style="margin-bottom:12px">
          <a class="btn" href="quiz-{lid}.html">🎧 Quiz de cette leçon</a>
        </div>
        <div class="toolbar">
          <input id="search" type="text" placeholder="Rechercher (PT ou FR)..." oninput="filterCards()" />
          <label><input id="quiz" type="checkbox" onchange="toggleQuiz()"> Mode Quiz (cacher FR)</label>
        </div>
        <div id="list" class="grid">{''.join(cards)}</div>
        """
        write_html(out_dir / f"lesson-{lid}.html", f"Leçon — {title}", f"ID : {lid}", body)
