
(function(){
  // Mobile nav toggle
  const t=document.querySelector('.nav-toggle');
  const list=document.getElementById('navLinks');
  if(t && list){ t.addEventListener('click',()=>{ const ex=t.getAttribute('aria-expanded')==='true'; t.setAttribute('aria-expanded', String(!ex)); list.classList.toggle('show'); }); }

  // Cookie bar
  const bar=document.getElementById('cookieBar');
  if(bar && !localStorage.getItem('cookieChoice')){ bar.hidden=false; }
  const acc=document.getElementById('cookieAccept');
  const ess=document.getElementById('cookieEssential');
  if(acc){ acc.onclick=()=>{ localStorage.setItem('cookieChoice','all'); bar.hidden=true; } }
  if(ess){ ess.onclick=()=>{ localStorage.setItem('cookieChoice','essential'); bar.hidden=true; } }

  // Home sections loader (10 items per category)
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

  function loadHome(){
    document.querySelectorAll('.home-section').forEach(section=>{
      const file=section.getAttribute('data-json');
      const grid=section.querySelector('.card-grid');
      fetch('data/'+file).then(r=>r.json()).then(items=>{
        (items||[]).slice(0,10).forEach(it=> grid.appendChild(renderCard(it)));
      }).catch(()=>{});
    });
  }

  if(document.body.classList.contains('home-body')||document.querySelector('.home')){
    loadHome();
  }
})();
