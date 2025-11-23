(function(){
  // update countdown to next local midnight
  function getNextMidnight(){
    const now = new Date();
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate()+1);
    return tomorrow; // midnight of next day local time
  }

  function formatDuration(ms){
    if(ms < 0) ms = 0;
    const totalSeconds = Math.floor(ms/1000);
    const hours = Math.floor(totalSeconds/3600);
    const minutes = Math.floor((totalSeconds%3600)/60);
    const seconds = totalSeconds%60;
    return [hours, minutes, seconds].map(n=>String(n).padStart(2,'0')).join(':');
  }

  function startCountdown(){
    const el = document.getElementById('daily-countdown');
    if(!el) return;
    let next = getNextMidnight();

    function tick(){
      const now = new Date();
      const diff = next - now;
      if(diff <= 0){
        // when day rolls over, refresh the page so server-side and templates update
        try{ window.location.reload(); }catch(e){ /* ignore */ }
        return;
      }
      el.textContent = formatDuration(diff);
    }

    // initial tick and interval
    tick();
    setInterval(tick, 1000);
  }

  // start when DOM ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', startCountdown);
  } else {
    startCountdown();
  }
})();
