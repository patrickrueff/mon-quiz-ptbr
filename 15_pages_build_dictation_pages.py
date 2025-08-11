# 15_pages_build_dictation_pages.py
from pathlib import Path
from utils_load_json import load_json
from pages_to_quiz_pool_js import to_quiz_pool_js
from pages_build_dictation_page import build_dictation_page

def build_dictation_pages(root: Path, out_dir: Path, lessons_index: dict, global_manifest: dict, dictation_js: str, timer_seconds: int = 12):
    # Dictée globale
    all_words = global_manifest.get("words", [])
    pool_js = to_quiz_pool_js(all_words)
    build_dictation_page(out_dir / "dictation.html", "Dictée — Tous les mots", "Écoute puis saisis exactement le mot/texte.", pool_js, dictation_js, timer_seconds)

    # Par leçon
    by_id = {w.get("id"): w for w in all_words if w.get("id")}
    for lid, _ in lessons_index.items():
        lesson = load_json(root / "lessons" / f"{lid}.json")
        title = lesson.get("title", lid)
        words = []
        for ref in lesson.get("words", []):
            w = by_id.get(ref.get("id"))
            if w: words.append(w)
        pool_js = to_quiz_pool_js(words)
        build_dictation_page(out_dir / f"dictation-{lid}.html", f"Dictée — {title}", f"Leçon : {lid}", pool_js, dictation_js, timer_seconds)
