/* STREAMIC — Homepage Loader (Stable) */

(() => {

  /* Card fade-in observer */
  const observer = new IntersectionObserver((entries)=>{
    entries.forEach(en=>{
      if (en.isIntersecting){
        en.target.classList.add("in-view");
      }
    });
  }, {threshold:0.1});

  /* Render card */
  function renderCard(i){
    const a = document.createElement('a');
    a.className = 'card';
    a.href = i.link;
    a.target='_blank';
    a.rel='noopener';

    const w = document.createElement('div');
    w.className = 'card-image';

    const img = document.createElement('img');
    img.src = 'assets/fallback.jpg';
    img.loading='lazy';

    if(i.image){
      const pre = new Image();
      pre.onload = ()=>{ img.src=i.image; img.classList.add("loaded"); };
      pre.src=i.image;
    } else {
      requestAnimationFrame(()=> img.classList.add("loaded"));
    }

    w.appendChild(img);
    a.appendChild(w);

    const b = document.createElement('div');
    b.className='card-body';

    const h = document.createElement('h3');
    h.textContent = i.title || 'Untitled';

    const s = document.createElement('span');
    s.className='source';
    s.textContent = i.source || '';

    b.appendChild(h);
    b.appendChild(s);
    a.appendChild(b);

    observer.observe(a);
    return a;
  }

  /* Load homepage sections */
  function loadHome(){
    document.querySelectorAll('.home-section').forEach(sec=>{
      const file = sec.getAttribute('data-json');
      const grid = sec.querySelector('.card-grid');

      fetch('data/'+file)
        .then(r=>r.json())
        .then(items=>{
          (items||[]).slice(0,10).forEach(it=>{
            grid.appendChild(renderCard(it));
          });
        })
        .catch(()=>{});
    });
  }

  if(document.querySelector('.home')){
    loadHome();
  }

})();
