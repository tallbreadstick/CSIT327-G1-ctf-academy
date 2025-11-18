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
  async function toggle(btn){
    const url = btn.getAttribute('data-toggle-url');
    try{
      const res = await fetch(url, {method: 'POST', headers:{'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With':'XMLHttpRequest'}});
      const data = await res.json();
      if(!res.ok || data.error){ throw new Error(data.error || 'Failed'); }
      const on = !!data.favorited;
      btn.dataset.favorited = on ? '1':'0';
      btn.setAttribute('aria-pressed', on ? 'true':'false');
      const i = btn.querySelector('i');
      if(i){
        i.classList.toggle('fas', on);
        i.classList.toggle('far', !on);
        i.classList.toggle('text-yellow-400', on);
        i.classList.toggle('text-gray-500', !on);
      }
    }catch(e){
      toast('Unable to save favorite. Please try again.');
    }
  }
  function bind(){
    document.querySelectorAll('[data-action="toggle-favorite"]').forEach(b=>{
      b.addEventListener('click', (e)=>{ e.preventDefault(); toggle(b); });
    });
  }
  document.addEventListener('DOMContentLoaded', bind);
})();
