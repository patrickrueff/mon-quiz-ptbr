# 09_pages_build_lesson_pages.py
# Génère les pages "leçon" en s'appuyant sur global_manifest["words"]
# - Chargement robuste des utilitaires (même si les fichiers commencent par un chiffre)
# - Intègre la phonétique via w.get("phon","") — identique à la logique des leçons
# - Ajoute un lien direct vers le quiz et la dictée de la leçon

from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
from typing import Any, Dict, List

# -----------------------------
# Chargement robuste d'un module
# -----------------------------
def _load_attr_from_candidates(attr_name: str, candidates: List[str]) -> Any:
    """
    Tente de charger `attr_name` depuis une liste de fichiers candidats (dans le même dossier que ce script).
    Chaque entrée de `candidates` est un nom de fichier .py ou un nom sans extension.
    Retourne l'attribut si trouvé, sinon lève ImportError.
    """
    here = Path(__file__).parent.resolve()

    for cand in candidates:
        # Normaliser en fichier .py
        filename = cand if cand.endswith(".py") else f"{cand}.py"
        path = here / filename
        if not path.exists():
            continue

        # Charger le module depuis un chemin de fichier, même si le nom commence par un chiffre
        mod_name = f"_dyn_{path.stem}"
        spec = importlib.util.spec_from_file_location(mod_name, str(path))
        if not spec or not spec.loader:
            continue

        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception:
            # On essaye le candidat suivant
            continue

        if hasattr(mod, attr_name):
            return getattr(mod, attr_name)

    # Si aucun candidat n'a fonctionné :
    tried = ", ".join(candidates)
    raise ImportError(f"Impossible de charger '{attr_name}' depuis: {tried}")

# -----------------------------
# Récupération des utilitaires
# -----------------------------
write_html = _load_attr_from_candidates(
    "write_html",
    [
        "utils_write_html",
        "06_utils_write_html",   # ex: fichier numéroté
    ],
)

build_word_card = _load_attr_from_candidates(
    "build_word_card",
    [
        "utils_build_word_card",
        "07_utils_build_word_card",
    ],
)

load_json = _load_attr_from_candidates(
    "load_json",
    [
        "utils_load_json",
        "05_utils_load_json",
    ],
)

# -----------------------------
# Générateur des pages de leçon
# -----------------------------
def build_lesson_pages(
    root: Path,
    out_dir: Path,
    lessons_index: Dict[str, Any],
    global_manifest: Dict[str, Any],
) -> None:
    """
    Génère une page HTML par leçon.

    Paramètres
    ----------
    root : Path
        Dossier racine contenant les données (ex: /lessons/*.json).
    out_dir : Path
        Dossier de sortie pour les pages HTML.
    lessons_index : dict
        Index des leçons { lesson_id: meta }. `meta` peut au minimum contenir le titre.
    global_manifest : dict
        Manifest global avec la clé 'words' :
        words: [
            {
                "id": <str>,
                "pt": <str>,
                "fr": <str>,
                "phon": <str>,                 # ← phonétique (clé alignée)
                "files": { "normal": <str>, "slow": <str> }
            },
            ...
        ]
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Index des mots par ID (source unique)
    by_id = {w.get("id"): w for w in (global_manifest.get("words") or []) if w.get("id")}

    for lid, meta in (lessons_index or {}).items():
        # Charger la définition de la leçon
        lesson_path = root / "lessons" / f"{lid}.json"
        lesson = load_json(lesson_path)

        # Titre : priorité à la leçon, puis meta, sinon fallback sur l'id
        title = lesson.get("title") or (meta.get("title") if isinstance(meta, dict) else None) or lid
        words = lesson.get("words") or []

        # Construire les cartes
        cards_html: List[str] = []
        for idx, ref in enumerate(words, start=1):
            # Chaque ref devrait ressembler à {"id": "..."} ; on mappe vers l'entrée du manifest
            word = by_id.get(ref.get("id")) if isinstance(ref, dict) else None
            if not word:
                continue

            files = word.get("files") or {}
            pt = word.get("pt", "")
            fr = word.get("fr", "")
            phon = word.get("phon", "")                # ← clé phon identique à celle lue par le quiz/dictée
            audio_normal = files.get("normal", "")
            audio_slow = files.get("slow", "")

            # build_word_card(index, pt, fr, phon, audio_normal, audio_slow)
            cards_html.append(
                build_word_card(idx, pt, fr, phon, audio_normal, audio_slow)
            )

        # Corps de page : actions + outils + grilles
        body = (
            f'<div class="actions" style="margin-bottom:12px">'
            f'  <a class="btn" href="quiz-{lid}.html">🎧 Quiz de cette leçon</a>'
            f'  <a class="btn" href="dictation-{lid}.html">⌨️ Dictée</a>'
            f'</div>'
            f'<div class="toolbar">'
            f'  <input id="search" type="text" placeholder="Rechercher (PT ou FR)..." oninput="filterCards()" />'
            f'  <label><input id="quiz" type="checkbox" onchange="toggleQuiz()"> Mode Quiz (cacher FR)</label>'
            f'</div>'
            f'<div id="list" class="grid">{"".join(cards_html)}</div>'
        )

        # Écriture du HTML
        out_file = out_dir / f"lesson-{lid}.html"
        write_html(out_file, f"Leçon — {title}", f"ID : {lid}", body)

# -----------------------------
# Exécution directe (optionnel)
# -----------------------------
if __name__ == "__main__":
    """
    Usage:
      python 09_pages_build_lesson_pages.py <root> <out_dir> <lessons_index.json> <global_manifest.json>
    """
    import json

    if len(sys.argv) < 5:
        print(
            "Usage:\n"
            "  python 09_pages_build_lesson_pages.py <root> <out_dir> <lessons_index.json> <global_manifest.json>"
        )
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    lessons_index_path = Path(sys.argv[3]).resolve()
    global_manifest_path = Path(sys.argv[4]).resolve()

    lessons_index = json.loads(lessons_index_path.read_text(encoding="utf-8"))
    global_manifest = json.loads(global_manifest_path.read_text(encoding="utf-8"))

    build_lesson_pages(root, out_dir, lessons_index, global_manifest)
    print(f"✅ Pages leçons générées dans : {out_dir}")
