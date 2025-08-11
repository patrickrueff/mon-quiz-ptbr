from html import escape

def build_word_card(idx, pt, fr, phon, file_normal, file_slow=""):
    pt_esc, fr_esc = escape(pt), escape(fr)
    phon_esc = escape(phon) if phon else ""
    btn_slow = f'<button onclick="play(\'{escape(file_slow)}\')">🐢 Lent</button>' if file_slow else ''
    return f"""    <div class="card" data-pt="{pt_esc.lower()}" data-fr="{fr_esc.lower()}">
      <div class="texts">
        <div class="label badge">{idx}</div>
        <div>
          <div class="pt">{pt_esc}</div>
          {f'<div class="phon">[{phon_esc}]</div>' if phon_esc else ''}
          <div class="fr">{fr_esc}</div>
        </div>
      </div>
      <div class="actions">
        <button onclick="play('{escape(file_normal)}')">▶️ Écouter</button>
        {btn_slow}
      </div>
    </div>
    """
