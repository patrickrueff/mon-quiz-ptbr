from pathlib import Path
from utils_load_json import load_json
from pages_to_quiz_pool_js import to_quiz_pool_js
from pages_build_quiz_page import build_quiz_page

def build_quiz_pages(root: Path, out_dir: Path, lessons_index: dict, global_manifest: dict, quiz_js: str, timer_seconds: int = 8):
    # global quiz
    all_words = global_manifest.get("words", [])
    pool_js = to_quiz_pool_js(all_words)
    build_quiz_page(out_dir / "quiz.html", "Quiz — Tous les mots", "Clique sur la bonne réponse après écoute.", pool_js, quiz_js, timer_seconds)

    # per-lesson
    by_id = {w.get("id"): w for w in all_words if w.get("id")}
    for lid, _ in lessons_index.items():
        lesson = load_json(root / "lessons" / f"{lid}.json")
        title = lesson.get("title", lid)
        words = []
        for ref in lesson.get("words", []):
            w = by_id.get(ref.get("id"))
            if w: words.append(w)
        pool_js = to_quiz_pool_js(words)
        build_quiz_page(out_dir / f"quiz-{lid}.html", f"Quiz — {title}", f"Leçon : {lid}", pool_js, quiz_js, timer_seconds)
