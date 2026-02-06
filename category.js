
let allItems=[]; let visible=0; const BATCH=6;

function renderCard(item){
  const a=document.createElement('a');
  a.className='card'; a.href=item.link; a.target='_blank'; a.rel='noopener';
  const imgWrap=document.createElement('div'); imgWrap.className='card-image';
  const img=document.createElement('img'); img.alt=item.source?('Image from '+item.source):'News image';
  img.src='assets/fallback.jpg'; img.loading='lazy';
  if(item.image){ const test=new Image(); test.onload=()=>img.src=item.image; test.src=item.image; }
  imgWrap.appendChild(img); a.appendChild(imgWrap);
  const body=document.createElement('div'); body.className='card-body';
  const h3=document.createElement('h3'); h3.textContent=item.title||'Untitled';
  const src=document.createElement('span'); src.className='source'; src.textContent=item.source||'';
  body.appendChild(h3); body.appendChild(src); a.appendChild(body);
  return a;
}

function showNext(){
  const grid=document.getElementById('content');
  allItems.slice(visible, visible+BATCH).forEach(i=> grid.appendChild(renderCard(i)));
  visible+=BATCH; if(visible>=allItems.length){ const b=document.getElementById('loadMoreBtn'); if(b) b.style.display='none'; }
}

function loadSingleCategory(jsonFile){
  fetch('data/'+jsonFile).then(r=>r.json()).then(items=>{ allItems=items||[]; visible=0; showNext(); });
}

document.addEventListener('DOMContentLoaded',()=>{
  const b=document.getElementById('loadMoreBtn'); if(b) b.addEventListener('click', showNext);
});
