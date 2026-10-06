'use strict';
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const menu=$('.menu-toggle'),nav=$('.site-nav');
function closeMenu(){if(!menu)return;nav.classList.remove('is-open');menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label','Open navigation')}
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';nav.classList.toggle('is-open',open);menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close navigation':'Open navigation')});
nav?.addEventListener('click',e=>{if(e.target.closest('a'))closeMenu()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav?.classList.contains('is-open')){closeMenu();menu.focus()}});
document.addEventListener('click',e=>{if(menu&&!nav.contains(e.target)&&!menu.contains(e.target))closeMenu()});
window.matchMedia('(min-width:851px)').addEventListener('change',e=>{if(e.matches)closeMenu()});
const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
if(!motion.matches&&'IntersectionObserver' in window){
 document.documentElement.classList.add('js-ready');const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.remove('is-waiting');observer.unobserve(entry.target)}}),{threshold:.04});
 $$('.reveal').forEach(el=>{if(el.getBoundingClientRect().top>innerHeight){el.classList.add('is-waiting');observer.observe(el)}});
}
const line=$('.scroll-line');let scheduled=false;
window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(()=>{const height=document.documentElement.scrollHeight-innerHeight;if(line)line.style.transform=`scaleX(${height>0?scrollY/height:0})`;scheduled=false})}},{passive:true});
$$('[data-top]').forEach(b=>b.addEventListener('click',()=>window.scrollTo({top:0,behavior:motion.matches?'instant':'smooth'})));
// An ordinary HTML catalog remains available if JavaScript is disabled.
const catalog=$('[data-catalog]');
if(catalog){
 const query=$('#product-search'),sort=$('#product-sort'),grid=$('#catalog-grid'),items=$$('[data-product]',grid),status=$('#catalog-status'),pagination=$('#pagination'),empty=$('#catalog-empty');
 let page=1;const pageSize=18;const original=items.slice();
 function render(){
  const q=query.value.trim().toLowerCase();let matching=original.filter(item=>item.dataset.search.includes(q));
  if(sort.value==='name')matching.sort((a,b)=>a.dataset.title.localeCompare(b.dataset.title));
  if(sort.value==='model')matching.sort((a,b)=>a.dataset.model.localeCompare(b.dataset.model)||a.dataset.title.localeCompare(b.dataset.title));
  const total=matching.length,pages=Math.max(1,Math.ceil(total/pageSize));page=Math.min(page,pages);items.forEach(item=>{item.hidden=true});
  const visible=matching.slice((page-1)*pageSize,page*pageSize);visible.forEach(item=>{item.hidden=false;grid.append(item)});
  status.textContent=total?`${(page-1)*pageSize+1}–${Math.min(page*pageSize,total)} of ${total} products`:'0 products';empty.hidden=total>0;
  pagination.replaceChildren();pagination.hidden=pages<=1;
  function button(label,target,disabled=false,current=false){const b=document.createElement('button');b.type='button';b.textContent=label;b.disabled=disabled;b.setAttribute('aria-label',typeof label==='number'?`Page ${label}`:label==='←'?'Previous page':'Next page');if(current)b.setAttribute('aria-current','page');b.addEventListener('click',()=>{page=target;render();query.scrollIntoView({block:'start',behavior:motion.matches?'instant':'smooth'});$('.pagination button[aria-current=page]')?.focus({preventScroll:true})});pagination.append(b)}
  button('←',page-1,page===1);let displayed=[1,page-1,page,page+1,pages].filter(n=>n>0&&n<=pages);displayed=[...new Set(displayed)].sort((a,b)=>a-b);
  displayed.forEach((n,i)=>{if(i&&n-displayed[i-1]>1){const gap=document.createElement('span');gap.textContent='…';gap.setAttribute('aria-hidden','true');pagination.append(gap)}button(n,n,false,n===page)});button('→',page+1,page===pages);
  const params=new URLSearchParams(location.search);q?params.set('q',query.value):params.delete('q');sort.value!=='featured'?params.set('sort',sort.value):params.delete('sort');if(page>1)params.set('page',page);else params.delete('page');history.replaceState(null,'',location.pathname+(params.size?'?'+params.toString():''));
 }
 const params=new URLSearchParams(location.search);query.value=params.get('q')||'';if(['name','model'].includes(params.get('sort')))sort.value=params.get('sort');page=Math.max(1,Number(params.get('page'))||1);
 query.addEventListener('input',()=>{page=1;render()});sort.addEventListener('change',()=>{page=1;render()});$('#clear-search')?.addEventListener('click',()=>{query.value='';page=1;render();query.focus()});render();
}
const gallery=$('[data-gallery]');
if(gallery){const main=$('#gallery-image');$$('[data-gallery-src]',gallery).forEach(button=>button.addEventListener('click',()=>{main.src=button.dataset.gallerySrc;main.alt=button.dataset.galleryAlt;$$('[data-gallery-src]',gallery).forEach(b=>b.setAttribute('aria-pressed',String(b===button)))}))}
const zoom=$('#image-zoom'),zoomImage=$('#zoom-image');
$$('[data-zoom-src]').forEach(button=>button.addEventListener('click',()=>{zoomImage.src=button.dataset.zoomSrc;zoomImage.alt=button.dataset.zoomAlt||'Document';zoom.showModal()}));
$('#gallery-zoom')?.addEventListener('click',()=>{zoomImage.src=$('#gallery-image').src;zoomImage.alt=$('#gallery-image').alt;zoom.showModal()});
$('#close-zoom')?.addEventListener('click',()=>zoom.close());zoom?.addEventListener('click',e=>{if(e.target===zoom)zoom.close()});
const form=$('#inquiry-form');
if(form){
 const params=new URLSearchParams(location.search);if(params.get('product'))$('#inquiry-product').value=params.get('product');
 form.addEventListener('input',()=>{$('#draft-preview').hidden=true;$('#copy-feedback').textContent=''});
 form.addEventListener('submit',e=>{
  e.preventDefault();if(!form.reportValidity())return;const f=new FormData(form);
  const subject=`KWS inquiry${f.get('product')?' — '+String(f.get('product')).slice(0,180):''}`;
  const draft=`Hello KWS team,\n\n${f.get('message')}\n\nProduct / model: ${f.get('product')||'Please advise'}\nQuantity: ${f.get('quantity')||'To be discussed'}\nName: ${f.get('name')}\nCompany: ${f.get('company')||'—'}\nEmail: ${f.get('email')}\nCountry / region: ${f.get('country')||'—'}\n\nThank you.`;
  $('#draft-text').value=draft;$('#draft-email').href=`mailto:mandyxu@scentairmachines.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(draft)}`;$('#draft-whatsapp').href=`https://wa.me/8613590491364?text=${encodeURIComponent(subject+'\n\n'+draft)}`;
  $('#draft-preview').hidden=false;$('#draft-heading').focus();$('#draft-preview').scrollIntoView({block:'center',behavior:motion.matches?'instant':'smooth'});
 });
 $('#copy-draft')?.addEventListener('click',async()=>{const draft=$('#draft-text');try{await navigator.clipboard.writeText(draft.value);$('#copy-feedback').textContent='Draft copied. Paste it into your preferred email app.'}catch{draft.focus();draft.select();$('#copy-feedback').textContent='Select and copy the draft, then paste it into your email app.'}});
}

const carousel=$('[data-carousel]');
if(carousel){
 const slides=$$('template[data-hero-slide]',carousel);let index=0,paused=motion.matches,timer;
 const pause=$('[data-carousel-pause]',carousel);
 const show=n=>{index=(n+slides.length)%slides.length;carousel.dataset.slide=String(index);const s=slides[index].content;$('#hero-title').innerHTML=$('.slide-title',s).innerHTML;$('#hero-copy').textContent=$('.slide-copy',s).textContent;$('#hero-label').textContent=$('.slide-label',s).textContent;const atmosphere=$('#hero-atmosphere');if(atmosphere)atmosphere.src=$('.slide-atmosphere',s).src;const img=$('.slide-image',s);$('#hero-image').src=img.src;$('#hero-image').alt=img.alt;const link=$('.slide-link',s);$('#hero-link').href=link.href;$('#hero-link').innerHTML=link.innerHTML;$('#carousel-status').textContent=`0${index+1} / 0${slides.length}`;$$('[data-carousel-index]',carousel).forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.carouselIndex)===index)))};
 const schedule=()=>{clearInterval(timer);pause.textContent=paused?'Play':'Pause';pause.setAttribute('aria-label',paused?'Play carousel':'Pause carousel');if(!paused&&!document.hidden&&!carousel.matches(':hover')&&!carousel.contains(document.activeElement))timer=setInterval(()=>show(index+1),6000)};
 $('.carousel-controls',carousel).hidden=false;
 $('[data-carousel-prev]',carousel).addEventListener('click',()=>show(index-1));$('[data-carousel-next]',carousel).addEventListener('click',()=>show(index+1));$$('[data-carousel-index]',carousel).forEach(b=>b.addEventListener('click',()=>show(Number(b.dataset.carouselIndex))));pause.addEventListener('click',()=>{paused=!paused;schedule()});carousel.addEventListener('mouseenter',schedule);carousel.addEventListener('mouseleave',schedule);carousel.addEventListener('focusin',schedule);carousel.addEventListener('focusout',()=>setTimeout(schedule,0));document.addEventListener('visibilitychange',schedule);motion.addEventListener('change',()=>{paused=motion.matches;schedule()});schedule();
}

function brandSceneProducts(root=document){$$('img.scene-product, #product-details img',root).forEach(img=>{if(img.parentElement.classList.contains('product-brand-frame'))return;const frame=document.createElement('span');frame.className='product-brand-frame';img.before(frame);frame.append(img)});}
brandSceneProducts();
if($('[data-gallery]'))$('#image-zoom')?.classList.add('product-zoom');
const showroom=$('[data-showroom]');
if(showroom){
 let scene='hotel',running=!motion.matches,inView=false;const schedule=$('#scene-schedule',showroom),play=$('[data-scene-play]',showroom),advice=$('.scene-advice',showroom),inquiry=$('[data-scene-inquiry]',showroom);
 const panels=$$('[data-scene-panel]',showroom),names={hotel:'Hotel lobby',office:'Workplace reception',washroom:'Shared washroom'};
 const briefing=()=>{const panel=panels.find(p=>p.dataset.scenePanel===scene),selected=$('[data-point][aria-pressed=true]',panel),detail=$(`template[data-point-detail="${selected.dataset.point}"]`,panel).content;const name=$('.point-product-name',detail).textContent;const preference=schedule.value==='business'?'Business hours':'Extended hours';const url=new URL(inquiry.href);url.searchParams.set('product',name);url.searchParams.set('brief',`I would like to discuss a ${names[scene].toLowerCase()} project.\nOperating preference: ${preference}.\nEquipment point: ${$('h3',detail).textContent}.\nPlease advise on suitable placement, model settings, compatibility and maintenance.`);inquiry.href=url.href;advice.textContent=schedule.value==='business'?'Business-hours preference: discuss a suitable schedule and the selected model’s timer options.':'Extended-hours preference: discuss operating limits, replenishment access and maintenance for the selected model.'};
 const renderMotion=()=>{showroom.classList.toggle('is-demonstrating',running&&inView&&!document.hidden&&!motion.matches);play.disabled=motion.matches;play.textContent=motion.matches?'Static preview · reduced motion':running?'Pause demonstration':'Start demonstration';play.setAttribute('aria-pressed',String(running));};
 const choosePoint=(panel,button)=>{const template=$(`template[data-point-detail="${button.dataset.point}"]`,panel);$('.point-details',panel).replaceChildren(template.content.cloneNode(true));brandSceneProducts(panel);$$('[data-point]',panel).forEach(b=>b.setAttribute('aria-pressed',String(b===button)));$('.scene-visual',panel).style.setProperty('--pulse-x',button.style.getPropertyValue('--x'));$('.scene-visual',panel).style.setProperty('--pulse-y',button.style.getPropertyValue('--y'));briefing()};
 $$('[data-scene]',showroom).forEach(button=>button.addEventListener('click',()=>{scene=button.dataset.scene;panels.forEach(p=>p.hidden=p.dataset.scenePanel!==scene);$$('[data-scene]',showroom).forEach(b=>b.setAttribute('aria-pressed',String(b===button)));briefing()}));
 panels.forEach(panel=>$$('[data-point]',panel).forEach(button=>button.addEventListener('click',()=>choosePoint(panel,button))));
 schedule.addEventListener('change',briefing);play.hidden=false;play.addEventListener('click',()=>{running=!running;renderMotion()});document.addEventListener('visibilitychange',renderMotion);motion.addEventListener('change',()=>{if(motion.matches)running=false;renderMotion()});if('IntersectionObserver' in window)new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;renderMotion()},{threshold:.12}).observe(showroom);briefing();renderMotion();
}
const briefingParam=new URLSearchParams(location.search).get('brief');if(form&&briefingParam)$('#inquiry-message').value=briefingParam.slice(0,2000);

// Floating customer-service entry using the verified company contacts.
const support=document.createElement('aside');
support.className='customer-support';support.setAttribute('aria-label','KWS customer service');
support.innerHTML=`<section class="support-panel" id="support-panel" aria-label="Contact KWS" hidden><div class="support-heading"><div><span class="support-label">KWS CUSTOMER SERVICE</span><h2>How can we help?</h2></div><button type="button" data-support-close aria-label="Close customer service">×</button></div><p>Discuss products, OEM / ODM requirements and your project with our team.</p><a class="support-link support-whatsapp" href="https://wa.me/8613590491364" target="_blank" rel="noopener">WhatsApp <span aria-hidden="true">↗</span></a><a class="support-link" href="mailto:mandyxu@scentairmachines.com">Email our team <span aria-hidden="true">↗</span></a><a class="support-link" href="/contact/">Send an inquiry <span aria-hidden="true">↗</span></a><p class="support-note">Choose a channel to contact us. Replies depend on team availability.</p></section><button type="button" class="support-toggle" aria-expanded="false" aria-controls="support-panel"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M21 11a9 9 0 0 1-9 9H7l-4 2V11a9 9 0 1 1 18 0Z"/><path d="M7 10h10M7 14h6"/></svg><span>Contact KWS</span></button>`;
document.body.append(support);
const supportToggle=$('.support-toggle',support),supportPanel=$('.support-panel',support);
function closeSupport(restore=false){supportPanel.hidden=true;supportToggle.setAttribute('aria-expanded','false');if(restore)supportToggle.focus()}
supportToggle.addEventListener('click',()=>{const open=supportPanel.hidden;supportPanel.hidden=!open;supportToggle.setAttribute('aria-expanded',String(open));if(open)$('[data-support-close]',support).focus()});
$('[data-support-close]',support).addEventListener('click',()=>closeSupport(true));
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!supportPanel.hidden)closeSupport(true)});
document.addEventListener('click',event=>{if(!support.contains(event.target)&&!supportPanel.hidden)closeSupport()});
