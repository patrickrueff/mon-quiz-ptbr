from html import escape
from pathlib import Path
from assets_base_css import get_base_css
from assets_base_js_common import get_base_js_common

def write_html(out_path: Path, title: str, subtitle: str, body_html: str, extra_js: str = "", home_link=True):
    home_btn = '<a class="btn" href="index.html">🏠 Accueil</a>' if home_link else ''
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <title>{escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>{get_base_css()}</style>
</head>
<body>
  <div class="container">
    <div class="row" style="justify-content:space-between;align-items:baseline">
      <h1>{escape(title)}</h1>
      <div class="row">{home_btn}</div>
    </div>
    <p class="sub">{escape(subtitle)}</p>
    {body_html}
  </div>
  <div class="footer">Pages statiques — ouvrez localement sans serveur.</div>
  <audio id="player" preload="auto"></audio>
  <script>{get_base_js_common()}</script>
  <script>{extra_js}</script>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")
