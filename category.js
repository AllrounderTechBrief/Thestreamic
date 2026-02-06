// category.js
(function(){
  // Reuse front-end effects from app.js if present
  const bind = window.__streamicBindCardEnhancements || ((c)=>{});

  function renderCard(i){
    const a = document.createElement('a');
    a.className = 'card';
    a.href = i.link; a.target = '_blank'; a.rel = 'noopener';

    const w = document.createElement('div'); w.className = 'card-image';
    const img = document.createElement('img');
    img.alt = i.source ? ('Image from ' + i.source) : 'News image';
    img.src = 'assets/fallback.jpg'; img.loading = 'lazy';
    if (i.image){
      const pre = new Image();
      pre.onload = () => { img.src = i.image; img.classList.add('loaded'); };
      pre.src = i.image;
    } else {
      requestAnimationFrame(()=>img.classList.add('loaded'));
    }
    w.appendChild(img); a.appendChild(w);

    const b = document.createElement('div'); b.className = 'card-body';
    const h = document.createElement('h3'); h.textContent = i.title || 'Untitled';
    const s = document.createElement('span'); s.className = 'source'; s.textContent = i.source || '';
    b.appendChild(h); b.appendChild(s); a.appendChild(b);

    bind(a);
    return a;
  }

  // Group loader for multiple sections on one category page
  window.loadCategoryGroup = function(groups){
    const all = [];
    let master = []; let loaded = 0;

    function appendChunk(targetId, items, count){
      const grid = document.getElementById(targetId);
      if (!grid) return;
      items.forEach(it => grid.appendChild(renderCard(it)));
    }

    // Fetch all groups first, then set up "Load more"
    Promise.all(groups.map(g =>
      fetch('data/' + g.file).then(r => r.json()).then(list => ({...g, list}))
    )).then(sections => {
      // First paint: 9 items per section (3x3)
      sections.forEach(sec => {
        const first = (sec.list || []).slice(0, 9);
        appendChunk(sec.target, first, first.length);
        // Track leftovers for Load more
        const rest = (sec.list || []).slice(9);
        all.push({ target: sec.target, rest, idx: 0 });
      });

      const btn = document.getElementById('loadMoreBtn');
      if (!btn) return;

      btn.onclick = () => {
        let painted = 0;
        all.forEach(sec => {
          if (sec.idx >= sec.rest.length) return;
          const next = sec.rest.slice(sec.idx, sec.idx + 9); // 3 rows per click/section
          appendChunk(sec.target, next, next.length);
          sec.idx += next.length;
          painted += next.length;
        });
        if (painted === 0) btn.style.display = 'none';
      };
    });
  };
})();
