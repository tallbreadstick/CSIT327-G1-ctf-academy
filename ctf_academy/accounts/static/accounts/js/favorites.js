// favorites.js - handle favorite toggles
(function(){
  function getCookie(name){
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if(parts.length === 2) return parts.pop().split(';').shift();
  }
  function toast(msg, ok=false){
    const el = document.createElement('div');
    el.className = `fixed bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded text-white text-sm z-[9999] ${ok?'bg-green-600':'bg-red-600'}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(()=>el.remove(), 2200);
  }
  function updateIconState(btn, on){
    btn.classList.toggle('favorite-on', on);
    const icon = btn.querySelector('i, svg');
    if(!icon) return;
    icon.classList.toggle('fas', on);
    icon.classList.toggle('far', !on);
    icon.classList.toggle('fa-solid', on);
    icon.classList.toggle('fa-regular', !on);
    icon.classList.toggle('text-yellow-400', on);
    icon.classList.toggle('text-gray-500', !on);
  }
  function applyState(btn, on){
    btn.dataset.favorited = on ? '1':'0';
    btn.setAttribute('aria-pressed', on ? 'true':'false');
    updateIconState(btn, on);
  }
  async function toggle(btn){
    if(btn.dataset.loading === '1') return;
    const url = btn.getAttribute('data-toggle-url');
    const previous = btn.dataset.favorited === '1';
    const optimistic = !previous;
    applyState(btn, optimistic);
    btn.dataset.loading = '1';
    try{
      const res = await fetch(url, {method: 'POST', headers:{'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With':'XMLHttpRequest'}});
      const data = await res.json();
      if(!res.ok || data.error || data.success === false){
        throw new Error(data.message || data.error || 'Failed');
      }
      const payload = data && typeof data === 'object' && 'data' in data ? data.data : data;
      const on = !!(payload && payload.favorited);
      applyState(btn, on);
    }catch(e){
      applyState(btn, previous);
      toast('Unable to save favorite. Please try again.');
    }finally{
      delete btn.dataset.loading;
    }
  }
  function bind(){
    document.querySelectorAll('[data-action="toggle-favorite"]').forEach(b=>{
      b.addEventListener('click', (e)=>{ e.preventDefault(); toggle(b); });
    });
  }
  document.addEventListener('DOMContentLoaded', bind);
})();
