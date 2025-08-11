
# -*- coding: utf-8 -*-
"""
Main entrypoint (numbered files). Python cannot import modules starting with digits,
so we dynamically load each numbered file and register it under a classic module
name (e.g. "utils_write_html").

Usage:
  python 01_main.py --root vocab_audio --out vocab_audio --title "Vocabulaire – PT-BR" --timer 8 --delay 900
"""
import argparse, sys
from pathlib import Path
import importlib.util

HERE = Path(__file__).parent

def _load(alias: str, filename: str):
    """Load module from numbered filename and register as `alias`."""
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod

# Load dependencies in order and with aliases expected by the page files
mod_names = [
    ("assets_base_css", "02_assets_base_css.py"),
    ("assets_base_js_common", "03_assets_base_js_common.py"),
    ("assets_quiz_js", "04_assets_quiz_js.py"),
    ("utils_load_json", "05_utils_load_json.py"),
    ("utils_write_html", "06_utils_write_html.py"),
    ("utils_build_word_card", "07_utils_build_word_card.py"),
    ("pages_build_index", "08_pages_build_index.py"),
    ("pages_build_lesson_pages", "09_pages_build_lesson_pages.py"),
    ("pages_to_quiz_pool_js", "10_pages_to_quiz_pool_js.py"),
    ("pages_build_quiz_page", "11_pages_build_quiz_page.py"),
    ("pages_build_quiz_pages", "12_pages_build_quiz_pages.py"),
]
mods = {alias: _load(alias, fname) for alias, fname in mod_names}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default="vocab_audio", help="Racine des manifestes/audios")
    ap.add_argument("--out",  type=str, default="", help="Dossier de sortie HTML (défaut: root)")
    ap.add_argument("--title", type=str, default="Vocabulaire – Portugais brésilien", help="Titre de l’index")
    ap.add_argument("--timer", type=int, default=8, help="Secondes par question (quiz)")
    ap.add_argument("--delay", type=int, default=900, help="Délai en ms avant d'enchaîner la question suivante")
    args = ap.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out) if args.out else root
    out_dir.mkdir(parents=True, exist_ok=True)

    # Use loaded modules
    load_json = mods["utils_load_json"].load_json
    build_index = mods["pages_build_index"].build_index
    build_lesson_pages = mods["pages_build_lesson_pages"].build_lesson_pages
    build_quiz_pages = mods["pages_build_quiz_pages"].build_quiz_pages
    make_quiz_js = mods["assets_quiz_js"].make_quiz_js

    mg = root / "manifest_global.json"
    li = root / "lessons" / "_index.json"
    if not mg.exists(): raise SystemExit(f"[ERREUR] introuvable : {mg}")
    if not li.exists(): raise SystemExit(f"[ERREUR] introuvable : {li}")

    global_manifest = load_json(mg)
    lessons_index   = load_json(li)

    build_index(root, out_dir, args.title, global_manifest, lessons_index)
    build_lesson_pages(root, out_dir, lessons_index, global_manifest)

    quiz_js = make_quiz_js(timer_seconds=args.timer, auto_delay_ms=args.delay)
    build_quiz_pages(root, out_dir, lessons_index, global_manifest, quiz_js=quiz_js, timer_seconds=args.timer)

    print("✅ Interface + Quiz générés")
    print(f" - Accueil : {out_dir / 'index.html'}")
    print(f" - Quiz global : {out_dir / 'quiz.html'}")
    print(f" - Quiz leçon : {out_dir}/quiz-<id>.html")

if __name__ == "__main__":
    main()
