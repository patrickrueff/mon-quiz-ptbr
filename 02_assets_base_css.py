def get_base_css() -> str:
    return """:root{
  --bg:#0b0f14;--card:#121821;--text:#eef3fb;--muted:#b8c0cc;--accent:#5aa0ff;--accent2:#8ad1ff;--border:#1e2632
}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  background:radial-gradient(1000px 600px at 20% -10%,#16202d 0%,#0b0f14 60%) no-repeat fixed,var(--bg);
  color:var(--text);padding:32px 16px 80px}
.container{max-width:1000px;margin:0 auto}
h1{margin:0 0 8px} h2{margin:22px 0 12px} .sub{color:var(--muted);margin:0 0 24px}
.card{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border:1px solid var(--border);border-radius:16px;padding:16px;display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center}
.badge{min-width:36px;height:36px;border-radius:10px;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--accent),var(--accent2));color:#0b0f14;font-weight:700;border:1px solid rgba(255,255,255,.2);
  box-shadow:0 6px 14px rgba(90,160,255,.35)}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.texts{display:flex;gap:12px;align-items:center}
.texts .label{display:grid;place-items:center}
.pt{font-size:18px;font-weight:700;line-height:1.2}
.phon{color:#9fb4cc;font-size:13px;margin-top:2px}
.fr{color:var(--muted);margin-top:2px;font-size:14px}
.actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
button,a.btn{border:1px solid var(--border);background:#0e141d;color:#eef3fb;border-radius:10px;padding:8px 12px;cursor:pointer;font-weight:600;
  transition:transform .05s ease,border-color .2s ease;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
button:hover,a.btn:hover{border-color:var(--accent)} button:active,a.btn:active{transform:translateY(1px)}
.small{font-size:12px;color:var(--muted)}
.footer{position:fixed;left:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);
  border-top:1px solid var(--border);padding:10px 16px;color:var(--muted);font-size:12px;display:flex;justify-content:center}
.toolbar{display:flex;gap:10px;align-items:center;margin:16px 0 20px;flex-wrap:wrap}
.toolbar input,.toolbar select{flex:1;min-width:220px;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:#0e141d;color:#eef3fb;outline:none}
.quiz-wrap{max-width:720px;margin:0 auto}
.quiz-card{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:14px}
.choice{border:1px solid var(--border);border-radius:10px;padding:10px 12px;cursor:pointer;background:#0e141d}
.choice.correct{border-color:#3ddc97} .choice.wrong{border-color:#ff6b6b}
.kpi{display:flex;gap:12px;flex-wrap:wrap}
.kpi .pill{padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:#0e141d;color:#eef3fb}
.timer{font-weight:700}
@media (max-width:640px){.card{grid-template-columns:1fr}.actions{justify-content:flex-start}}
"""
