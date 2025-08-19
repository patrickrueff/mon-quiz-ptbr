#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
find_sql_queries_v2.py
- Ignore par défaut les fichiers temporaires (~vs*.sql), les dossiers backup VS et les fichiers 0 octet
- Déduplication par hash (lecture partielle 4 Mo)
- Classe l'origine (temp, backup_vs, normal)
- Export CSV trié par date modif décroissante
- Optionnel: copie des fichiers trouvés vers un dossier cible (flat ou arborescence)
"""

import argparse, csv, datetime as dt, hashlib, os, re, shutil, sys
from pathlib import Path

DEFAULT_EXCLUDES_PATH_PREFIXES = {
    r"C:\Windows",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\ProgramData",
    r"C:\$Recycle.Bin",
    r"C:\Recovery",
    r"C:\PerfLogs",
}
# motifs à ignorer (chemin complet, insensible à la casse)
IGNORE_PATTERNS = [
    r"\\AppData\\Local\\Temp\\~vs.*\.sql$",                 # fichiers temp VS
    r"\\Visual Studio 20\d{2}\\Backup Files\\",             # dossiers backup VS
]
IGNORE_REGEXES = [re.compile(p, re.IGNORECASE) for p in IGNORE_PATTERNS]

# T-SQL (SQL Server)
TSQL_PATTERNS = [
    r"\bCREATE\s+PROCEDURE\b", r"\bALTER\s+PROCEDURE\b", r"\bCREATE\s+FUNCTION\b",
    r"\bCREATE\s+VIEW\b", r"\bCREATE\s+TRIGGER\b",
    r"\bBEGIN\s+TRAN(\s+SACTION)?\b", r"\bCOMMIT\s+TRAN(\s+SACTION)?\b", r"\bROLLBACK\s+TRAN(\s+SACTION)?\b",
    r"\bSELECT\b.*\bFROM\b", r"\bINSERT\s+INTO\b", r"\bUPDATE\b\s+\w+\s+\bSET\b",
    r"\bDELETE\s+FROM\b", r"\bMERGE\s+INTO\b",
    r"\bWITH\s+\(\s*NOLOCK\s*\)", r"\bRAISERROR\b|\bTHROW\b",
    r"\bIDENTITY\(", r"\bNVARCHAR\b|\bVARCHAR\b|\bINT\b|\bBIT\b|\bDATETIME2?\b",
    r"\bUSE\s+\[?\w+\]?\b",
]
TSQL_REGEX = re.compile("|".join(TSQL_PATTERNS), re.IGNORECASE | re.DOTALL)

def looks_like_tsql(text: str) -> bool:
    return bool(TSQL_REGEX.search(text))

def read_sample(path: Path, max_bytes=1024*1024) -> str:
    try:
        with open(path, "rb") as f:
            return f.read(max_bytes).decode("utf-8", errors="ignore")
    except Exception:
        return ""

def quick_hash(path: Path, max_bytes=4*1024*1024) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            chunk = f.read(max_bytes)
            h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def classify_origin(p: Path) -> str:
    s = str(p)
    if re.search(r"\\AppData\\Local\\Temp\\~vs.*\.sql$", s, re.IGNORECASE):
        return "temp_vs"
    if re.search(r"\\Visual Studio 20\d{2}\\Backup Files\\", s, re.IGNORECASE):
        return "backup_vs"
    return "normal"

def should_ignore_by_pattern(path: Path, allow_temp: bool, allow_backups: bool) -> bool:
    if allow_temp and allow_backups:
        return False
    for rx in IGNORE_REGEXES:
        if rx.search(str(path)):
            # si l'utilisateur autorise ce type, on ne l'ignore pas
            if "Temp" in rx.pattern and allow_temp:
                continue
            if "Backup Files" in rx.pattern and allow_backups:
                continue
            return True
    return False

def is_recent(path: Path, threshold: dt.datetime, use_mtime: bool):
    st = path.stat()
    ref = st.st_mtime if use_mtime else st.st_ctime
    return dt.datetime.fromtimestamp(ref) >= threshold, st

def parse_args():
    ap = argparse.ArgumentParser(description="Trouver, filtrer et dédupliquer des requêtes SQL récentes.")
    ap.add_argument("--roots", nargs="*", default=None, help="Racines à scanner (ex: C:\\Users\\ICG332 D:\\Projets). Par défaut: C:\\ sous Windows.")
    ap.add_argument("--days", type=int, default=30, help="Fenêtre en jours (création ou modification).")
    ap.add_argument("--use-mtime", action="store_true", help="Utilise la date de modification (sinon : création).")
    ap.add_argument("--ext", type=str, default=".sql,.tsql", help="Extensions (séparées par virgules).")
    ap.add_argument("--require-tsql", action="store_true", help="Ne garder que les fichiers contenant du T-SQL.")
    ap.add_argument("--include-temp", action="store_true", help="Inclure les fichiers temporaires VS (~vs*.sql).")
    ap.add_argument("--include-backups", action="store_true", help="Inclure les backups Visual Studio.")
    ap.add_argument("--no-default-excludes", action="store_true", help="Ne pas exclure les dossiers système par défaut.")
    ap.add_argument("--copy-to", type=str, default=None, help="Copier les fichiers retenus vers ce dossier.")
    ap.add_argument("--preserve-tree", action="store_true", help="Préserver l’arborescence relative dans --copy-to.")
    ap.add_argument("--out", type=str, default=None, help="CSV de sortie (défaut: ./sql_recents_YYYYMMDD_HHMMSS.csv)")
    return ap.parse_args()

def detect_default_roots():
    if os.name == "nt":
        return [Path("C:\\")]
    return [Path.home()]

def main():
    args = parse_args()
    roots = [Path(r) for r in (args.roots if args.roots else detect_default_roots())]
    exts = {"."+e.strip().lower().lstrip(".") for e in args.ext.split(",") if e.strip()}
    excludes = set() if args.no_default_excludes else DEFAULT_EXCLUDES_PATH_PREFIXES
    threshold = dt.datetime.now() - dt.timedelta(days=args.days)

    results = []
    seen_hashes = set()

    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            # exclusions de base + dossiers cachés
            dirpath_p = Path(dirpath)
            if any(str(dirpath_p).startswith(pfx) for pfx in excludes):
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

            for fn in filenames:
                # extension
                ext = ("."+fn.rsplit(".",1)[-1].lower()) if "." in fn else ""
                if exts and ext not in exts:
                    continue

                p = dirpath_p / fn
                try:
                    # filtrage patterns temp/backup
                    if should_ignore_by_pattern(p, allow_temp=args.include_temp, allow_backups=args.include_backups):
                        continue

                    recent, st = is_recent(p, threshold, args.use_mtime)
                    if not recent:
                        continue
                    if st.st_size == 0:
                        continue  # ignore 0 octet

                    # lecture-échantillon
                    sample = read_sample(p)
                    if args.require_tsql and not looks_like_tsql(sample):
                        continue

                    origin = classify_origin(p)
                    h = quick_hash(p)
                    if h and h in seen_hashes:
                        # doublon probable (même contenu)
                        continue
                    if h:
                        seen_hashes.add(h)

                    # aperçu (1ère ligne non vide)
                    preview = ""
                    for line in sample.splitlines():
                        if line.strip():
                            preview = line.strip()[:240]
                            break

                    results.append({
                        "path": str(p),
                        "size_bytes": st.st_size,
                        "created": dt.datetime.fromtimestamp(st.st_ctime).isoformat(sep=" "),
                        "modified": dt.datetime.fromtimestamp(st.st_mtime).isoformat(sep=" "),
                        "extension": ext,
                        "origin": origin,         # temp_vs | backup_vs | normal
                        "a_ts_sql": looks_like_tsql(sample) if sample else False,
                        "hash_prefix": h[:12] if h else "",
                        "preview": preview
                    })

                except (PermissionError, FileNotFoundError):
                    continue
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
                    continue

    # tri: modifié desc
    results.sort(key=lambda r: r["modified"], reverse=True)

    # écriture CSV
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(args.out) if args.out else Path(f"sql_recents_{ts}.csv")
    fields = ["path","size_bytes","created","modified","extension","origin","a_ts_sql","hash_prefix","preview"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)

    print(f"[OK] {len(results)} fichier(s) retenu(s). CSV: {out.resolve()}")

    # copie optionnelle
    if args.copy_to and results:
        dest_root = Path(args.copy_to)
        dest_root.mkdir(parents=True, exist_ok=True)
        copied = 0
        for r in results:
            src = Path(r["path"])
            try:
                if args.preserve_tree:
                    # reconstruire chemin relatif à la racine scannée la plus longue qui matche
                    base = max((root for root in roots if str(src).lower().startswith(str(root).lower())),
                               key=lambda p: len(str(p)), default=roots[0])
                    rel = src.relative_to(base)
                    target = dest_root / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                else:
                    target = dest_root / src.name
                if not target.exists():
                    shutil.copy2(src, target)
                copied += 1
            except Exception as e:
                print(f"[WARN] copie échouée {src} -> {e}", file=sys.stderr)
        print(f"[OK] Copie terminée: {copied} fichier(s) vers {dest_root.resolve()}")

if __name__ == "__main__":
    main()
