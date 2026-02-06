/* STREAMIC — Category Loader (Stable) */

(function(){

  function renderCard(i){
    const a = document.createElement('a');
    a.className='card';
    a.href=i.link;
    a.target='_blank';
    a.rel='noopener';

    const w=document.createElement('div');
    w.className='card-image';

    const img=document.createElement('img');
    img.src='assets/fallback.jpg';
    img.loading='lazy';

    if(i.image){
      const pre=new Image();
      pre.onload=()=>{ img.src=i.image; img.classList.add("loaded"); };
      pre.src=i.image;
    } else {
      requestAnimationFrame(()=>img.classList.add("loaded"));
    }

    w.appendChild(img);
    a.appendChild(w);

    const b=document.createElement('div');
    b.className='card-body';

    const h=document.createElement('h3');
    h.textContent=i.title||'Untitled';

    const s=document.createElement('span');
    s.className='source';
    s.textContent=i.source||'';

    b.appendChild(h);
    b.appendChild(s);
    a.appendChild(b);

    return a;
  }

  window.loadSingleCategory = function(file){
    const grid=document.getElementById('content');
    const btn=document.getElementById('loadMoreBtn');

    let all=[]; let idx=0;
    const CHUNK=9; // 3 rows of 3

    function paint(){
      const slice = all.slice(idx, idx+CHUNK);
      slice.forEach(it=> grid.appendChild(renderCard(it)));
      idx+=slice.length;
      if(idx>=all.length && btn) btn.style.display='none';
    }

    fetch('data/'+file)
      .then(r=>r.json())
      .then(items=>{
        all=items||[];
        paint();
      });

    if(btn){
      btn.onclick = paint;
    }
  };

})();
