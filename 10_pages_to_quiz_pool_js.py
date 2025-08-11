import json

def to_quiz_pool_js(words_list):
    """
    Construit le POOL du quiz à partir d'une liste d'entrées vocab.
    Chaque entrée attendue peut contenir :
      - pt (str) : mot/phrase en portugais
      - fr (str) : traduction française
      - phon (str) : phonétique (même clé que pour les leçons)
      - files.normal (str) : chemin du fichier audio "normal"

    Retourne une chaîne JSON (pour injection côté JS).
    """
    arr = []
    for w in words_list:
        files = w.get("files", {}) or {}
        normal = files.get("normal")
        if not normal:
            # On ne prend que les entrées avec un audio "normal"
            continue

        arr.append({
            "pt":    w.get("pt", ""),
            "fr":    w.get("fr", ""),
            "phon":  w.get("phon", ""),   # ← phonétique alignée sur les leçons
            "normal": normal
        })

    return json.dumps(arr, ensure_ascii=False)
