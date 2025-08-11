import json

def to_quiz_pool_js(words_list):
    arr = []
    for w in words_list:
        files = w.get("files", {})
        normal = files.get("normal")
        if not normal: continue
        arr.append({"pt": w.get("pt",""), "fr": w.get("fr",""), "normal": normal})
    return json.dumps(arr, ensure_ascii=False)
