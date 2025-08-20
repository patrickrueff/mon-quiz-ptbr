# -*- coding: utf-8 -*-
"""
Génère un mp3 par mot (pt-BR) + manifestes, à partir de:
  - plan/vocab.json    : [{"pt","fr","phon"?,"id"?}, ...]
  - plan/lessons.json  : [{"id","title","words":[id|pt]}, ...]

Nouveautés:
  - support du champ "phon" (phonétique, affichée dans l'interface)
  - inchangé: ne régénère pas un mp3 s'il existe (sauf --force)
"""

import argparse, hashlib, json, re
from pathlib import Path
from typing import Dict, List, Tuple
from gtts import gTTS

def slugify(text: str) -> str:
    import unicodedata
    t = unicodedata.normalize('NFKD', text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "mot"

def stable_key(text: str) -> str:
    s = slugify(text)
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{s}-{h}"

def say_pt(text_pt: str, outpath: Path, slow: bool = False):
    outpath.parent.mkdir(parents=True, exist_ok=True)
    tts = gTTS(text=text_pt, lang="pt-br", slow=slow)
    tts.save(str(outpath))

def load_vocab(vocab_path: Path) -> List[Dict]:
    data = json.loads(vocab_path.read_text(encoding="utf-8"))
    rows = []
    for it in data:
        if not isinstance(it, dict): continue
        pt = (it.get("pt") or "").strip()
        fr = (it.get("fr") or "").strip()
        phon = (it.get("phon") or "").strip()
        cid = (it.get("id") or stable_key(pt)).strip() if pt else ""
        if pt and fr:
            rows.append({"id": cid, "pt": pt, "fr": fr, "phon": phon})
    return rows

def load_lessons(lessons_path: Path) -> List[Dict]:
    data = json.loads(lessons_path.read_text(encoding="utf-8"))
    lessons = []
    for it in data:
        lid = (it.get("id") or "").strip()
        title = (it.get("title") or "").strip()
        words = it.get("words") or []
        if lid and title:
            lessons.append({"id": lid, "title": title, "words": words})
    return lessons

def build_vocab_index(vocab_rows: List[Dict]) -> Tuple[Dict[str, Dict], Dict[str, str]]:
    by_id = {r["id"]: r for r in vocab_rows}
    pt_to_id: Dict[str, str] = {}
    for r in vocab_rows:
        pt_to_id.setdefault(r["pt"], r["id"])
    return by_id, pt_to_id

def generate_audios(by_id: Dict[str, Dict], out_dir: Path, slow=False, force=False) -> Dict[str, Dict]:
    audio_dir = out_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    result: Dict[str, Dict] = {}
    for i, (wid, item) in enumerate(by_id.items(), start=1):
        pt, fr, phon = item["pt"], item["fr"], item.get("phon","")
        base = f"{i:04d}-{wid}"
        file_normal = audio_dir / f"{base}.mp3"
        file_slow   = audio_dir / f"{base}-slow.mp3"

        if force or not file_normal.exists():
            print(f"🔊 {pt} -> {file_normal.name}")
            say_pt(pt, file_normal, slow=False)
        else:
            print(f"⏭️  {file_normal.name} déjà présent")
        files = {"normal": f"audio/{file_normal.name}"}

        if slow:
            if force or not file_slow.exists():
                print(f"🐢 {pt} -> {file_slow.name}")
                say_pt(pt, file_slow, slow=True)
            files["slow"] = f"audio/{file_slow.name}"

        result[wid] = {"id": wid, "pt": pt, "fr": fr, "phon": phon, "files": files}
    return result

def build_lesson_manifests(lessons, by_id, out_dir: Path, pt_to_id, fail_on_missing=False):
    lessons_dir = out_dir / "lessons"
    lessons_dir.mkdir(parents=True, exist_ok=True)
    index = {}
    for lec in lessons:
        lid, title, refs = lec["id"], lec["title"], lec["words"]
        resolved_ids, missing = [], []
        for ref in refs:
            rid = ref if ref in by_id else pt_to_id.get(ref, "")
            if rid: resolved_ids.append(rid)
            else:   missing.append(ref)
        if missing:
            msg = f"⚠️ Leçon '{lid}': références introuvables {missing}"
            if fail_on_missing: raise SystemExit(msg)
            else: print(msg)
        manifest = {"id": lid, "title": title, "words": [{"id": x} for x in resolved_ids]}
        (lessons_dir / f"{lid}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        index[lid] = manifest
    (lessons_dir / "_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vocab", type=str, default="plan/vocab.json")
    ap.add_argument("--lessons", type=str, default="plan/lessons.json")
    ap.add_argument("--out", type=str, default="vocab_audio")
    ap.add_argument("--slow", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--fail-on-missing", action="store_true")
    args = ap.parse_args()

    vocab_rows = load_vocab(Path(args.vocab))
    by_id, pt_to_id = build_vocab_index(vocab_rows)

    out_dir = Path(args.out)
    words_manifest = generate_audios(by_id, out_dir, slow=args.slow, force=args.force)

    global_manifest = {"version": 2, "count": len(words_manifest), "words": list(words_manifest.values())}
    (out_dir / "manifest_global.json").write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    lessons = load_lessons(Path(args.lessons))
    build_lesson_manifests(lessons, by_id, out_dir, pt_to_id, fail_on_missing=args.fail_on_missing)

    print("\n✅ Terminé")
    print(f"📄 {out_dir / 'manifest_global.json'}")
    print(f"📁 {out_dir / 'lessons'}")

if __name__ == "__main__":
    main()
