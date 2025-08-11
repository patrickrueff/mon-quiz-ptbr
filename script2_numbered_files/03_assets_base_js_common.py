def get_base_js_common() -> str:
    return """const player = document.getElementById('player');
function play(src){ player.src = src; player.play(); }
function stopAudio(){ try{ player.pause(); player.currentTime = 0; }catch(e){} }
function filterCards(){
  const q=(document.getElementById('search')?.value||'').trim().toLowerCase();
  const cards=document.querySelectorAll('#list .card');
  if(!q){ cards.forEach(c=>c.style.display=''); return; }
  cards.forEach(c=>{
    const pt=c.getAttribute('data-pt'), fr=c.getAttribute('data-fr');
    c.style.display = (pt.includes(q) || fr.includes(q)) ? '' : 'none';
  });
}
function toggleQuiz(){
  const chk=document.getElementById('quiz');
  const frs=document.querySelectorAll('.fr');
  frs.forEach(el=>{ el.style.visibility = chk.checked ? 'hidden' : 'visible'; });
}
"""
