(()=>{
'use strict';
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
document.querySelectorAll('video[data-hls]').forEach(player=>{
 const preview=player.hasAttribute('data-preview'),button=player.parentElement.querySelector('.preview-toggle');let ready=false,hls,visible=false,userPaused=reduced.matches;
 const failure=()=>{const error=document.querySelector('#video-error');if(!preview&&error)error.hidden=false;if(button){button.hidden=true}player.pause()};
 const label=()=>{if(button){button.textContent=player.paused?'Play':'Pause';button.setAttribute('aria-label',player.paused?'Play muted preview':'Pause preview')}};
 const init=()=>{if(ready)return;ready=true;if(preview)player.muted=true;
  if(player.canPlayType('application/vnd.apple.mpegurl')){player.src=player.dataset.hls;player.addEventListener('error',failure)}
  else if(window.Hls?.isSupported()){hls=new Hls({autoStartLoad:true,maxBufferLength:10,maxMaxBufferLength:20,enableWorker:false});hls.loadSource(player.dataset.hls);hls.attachMedia(player);hls.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal)failure()});window.addEventListener('pagehide',()=>hls.destroy(),{once:true})}else failure();
 };
 const sync=()=>{if(preview&&visible&&!userPaused&&!document.hidden){init();hls?.startLoad();player.play().catch(label)}else if(preview){player.pause();hls?.stopLoad()}label()};
 player.addEventListener('play',label);player.addEventListener('pause',label);
 if(preview){button?.addEventListener('click',()=>{userPaused=!player.paused;visible=true;sync()});new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()},{threshold:.35}).observe(player);document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',()=>{userPaused=reduced.matches;sync()});label()}
 else init();
});
})();
