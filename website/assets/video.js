(()=>{
'use strict';
const player=document.querySelector('video[data-hls]');
if(player){
 const source=player.dataset.hls;const failure=()=>{document.querySelector('#video-error').hidden=false};
 if(player.canPlayType('application/vnd.apple.mpegurl')){player.src=source;player.addEventListener('error',failure)}
 else if(window.Hls?.isSupported()){
  const hls=new Hls({autoStartLoad:true,maxBufferLength:10,maxMaxBufferLength:20,enableWorker:false});hls.loadSource(source);hls.attachMedia(player);
  player.addEventListener('play',()=>hls.startLoad(),{once:true});hls.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal)failure()});window.addEventListener('pagehide',()=>hls.destroy(),{once:true});
 }else failure();
}

})();
