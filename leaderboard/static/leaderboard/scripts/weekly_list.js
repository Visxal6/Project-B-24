(function(){
  // countdown to next Monday midnight local time
  function getNextWeekReset(){
    const now = new Date();
    const day = now.getDay(); // 0 sunday, 1 monday
    // compute days until next monday
    const daysUntilNextMonday = ((8 - day) % 7) || 7; // ensures at least 1 day
    const nextMonday = new Date(now.getFullYear(), now.getMonth(), now.getDate()+daysUntilNextMonday);
    return nextMonday; // next monday midnight local time
  }

  function formatDuration(ms){
    if(ms < 0) ms = 0;
    const totalSeconds = Math.floor(ms/1000);
    const days = Math.floor(totalSeconds / (3600*24));
    const hours = Math.floor((totalSeconds % (3600*24)) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    if(days > 0) return `${String(days).padStart(2,'0')}:${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
    return `${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
  }

  function startCountdown(){
    const el = document.getElementById('weekly-countdown');
    if(!el) return;
    let target = getNextWeekReset();

    function tick(){
      const now = new Date();
      const diff = target - now;
      if(diff <= 0){
        try{ window.location.reload(); }catch(e){}
        return;
      }
      el.textContent = formatDuration(diff);
    }
    tick();
    setInterval(tick, 1000);
  }

  // file preview for proof inputs
  function installPreviewHandlers(){
    const inputs = document.querySelectorAll('input[type=file][name=proof]');
    for(const input of inputs){
      input.addEventListener('change', (e) => {
        const file = input.files && input.files[0];
        const idx = input.dataset.idx;
        const previewEl = document.getElementById('preview-' + idx);
        if(!previewEl) return;
        if(!file){
          previewEl.style.backgroundImage = '';
          previewEl.setAttribute('aria-hidden','true');
          return;
        }
        const reader = new FileReader();
        reader.onload = function(ev){
          previewEl.style.backgroundImage = `url('${ev.target.result}')`;
          previewEl.style.backgroundSize = 'cover';
          previewEl.style.backgroundPosition = 'center';
          previewEl.setAttribute('aria-hidden','false');
        };
        reader.readAsDataURL(file);
      });
    }
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ startCountdown(); installPreviewHandlers(); });
  } else {
    startCountdown();
    installPreviewHandlers();
  }
})();
