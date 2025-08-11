# -*- coding: utf-8 -*-
"""
Main entrypoint (numéroté) sans arguments en ligne de commande.
Tous les paramètres sont définis directement ci-dessous.
- Génère : index, pages leçons, quiz (QCM) global & par leçon, dictée globale & par leçon.
"""
from pathlib import Path
import sys
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

# Chargement des modules nécessaires
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
    # --- Nouveaux modules : Dictée ---
    ("assets_dictation_js", "13_assets_dictation_js.py"),
    ("pages_build_dictation_page", "14_pages_build_dictation_page.py"),
    ("pages_build_dictation_pages", "15_pages_build_dictation_pages.py"),
]
mods = {alias: _load(alias, fname) for alias, fname in mod_names}

# ==== PARAMÈTRES PAR DÉFAUT ====
ROOT_DIR   = Path("vocab_audio")   # Racine des manifestes/audios
OUT_DIR    = ROOT_DIR              # Dossier de sortie HTML
TITLE      = "Vocabulaire – PT-BR" # Titre affiché sur la page d'accueil

# Quiz QCM
TIMER      = 8                     # Secondes par question (quiz QCM)
DELAY      = 900                   # Délai en ms avant d'enchaîner (QCM)

# Dictée
DICT_TIMER  = 12                   # Secondes par item (dictée)
DICT_REVEAL = 1500                 # ms d’affichage du feedback avant “Suivant” (dictée)

def main():
    root = ROOT_DIR
    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    load_json            = mods["utils_load_json"].load_json
    build_index          = mods["pages_build_index"].build_index
    build_lesson_pages   = mods["pages_build_lesson_pages"].build_lesson_pages
    build_quiz_pages     = mods["pages_build_quiz_pages"].build_quiz_pages
    make_quiz_js         = mods["assets_quiz_js"].make_quiz_js
    # Dictée
    build_dictation_pages = mods["pages_build_dictation_pages"].build_dictation_pages
    make_dictation_js     = mods["assets_dictation_js"].make_dictation_js

    mg = root / "manifest_global.json"
    li = root / "lessons" / "_index.json"
    if not mg.exists():
        raise SystemExit(f"[ERREUR] introuvable : {mg}")
    if not li.exists():
        raise SystemExit(f"[ERREUR] introuvable : {li}")

    global_manifest = load_json(mg)
    lessons_index   = load_json(li)

    # Pages de contenu
    build_index(root, out_dir, TITLE, global_manifest, lessons_index)
    build_lesson_pages(root, out_dir, lessons_index, global_manifest)

    # Quiz QCM
    quiz_js = make_quiz_js(timer_seconds=TIMER, auto_delay_ms=DELAY)
    build_quiz_pages(root, out_dir, lessons_index, global_manifest, quiz_js=quiz_js, timer_seconds=TIMER)

    # Dictée
    dictation_js = make_dictation_js(timer_seconds=DICT_TIMER, reveal_delay_ms=DICT_REVEAL)
    build_dictation_pages(root, out_dir, lessons_index, global_manifest, dictation_js=dictation_js, timer_seconds=DICT_TIMER)

    print("✅ Interface générée avec succès")
    print(f" - Accueil            : {out_dir / 'index.html'}")
    print(f" - Quiz global (QCM)  : {out_dir / 'quiz.html'}")
    print(f" - Dictée globale     : {out_dir / 'dictation.html'}")
    print(f" - Quiz par leçon     : {out_dir}/quiz-<id>.html")
    print(f" - Dictée par leçon   : {out_dir}/dictation-<id>.html")

if __name__ == "__main__":
    main()

## https://github.com/patrickrueff/mon-quiz-ptbr.git
