/* =========================================================
   STREAMIC — Category utilities (tabs + filters + load more)
   ========================================================= */
(function () {
  // Hook from app.js for fade-in / tilt / parallax
  const bindEnhance = window.__streamicBindCardEnhancements || ((c)=>{});

  // Render one card
  function renderCard(i) {
    const a = document.createElement('a');
    a.className = 'card';
    a.href = i.link; a.target = '_blank'; a.rel = 'noopener';

    const w = document.createElement('div'); w.className = 'card-image';
    const img = document.createElement('img');
    img.alt = i.source ? ('Image from ' + i.source) : 'News image';
    img.src = 'assets/fallback.jpg'; img.loading = 'lazy';

    if (i.image) {
      const pre = new Image();
      pre.onload = () => { img.src = i.image; img.classList.add('loaded'); };
      pre.src = i.image;
    } else {
      requestAnimationFrame(() => img.classList.add('loaded'));
    }

    w.appendChild(img); a.appendChild(w);

    const b = document.createElement('div'); b.className = 'card-body';
    const h = document.createElement('h3'); h.textContent = i.title || 'Untitled';
    const s = document.createElement('span'); s.className = 'source'; s.textContent = i.source || '';
    b.appendChild(h); b.appendChild(s); a.appendChild(b);

    bindEnhance(a);
    return a;
  }

  /* =========================================================
     SINGLE CATEGORY (legacy pages)
  ========================================================= */
  window.loadSingleCategory = function(file){
    const grid = document.getElementById('content');
    const btn  = document.getElementById('loadMoreBtn');
    if (!grid) return;

    let all = []; let idx = 0; const CHUNK = 9;

    function paintMore(){
      const slice = all.slice(idx, idx + CHUNK);
      slice.forEach(item => grid.appendChild(renderCard(item)));
      idx += slice.length;
      if (idx >= all.length && btn) btn.style.display = 'none';
    }

    fetch('data/' + file)
      .then(r => r.json())
      .then(items => { all = items || []; paintMore(); })
      .catch(()=>{});

    if (btn) btn.addEventListener('click', paintMore);
  };

  /* =========================================================
     EDIT & POST — TABS + BRAND CHIPS + LOAD MORE
  ========================================================= */
  window.initEditPostPage = function(){
    // Tab → file mapping
    const TAB_CFG = {
      vfx:      { file: 'out-3d-vfx.json',   grid: 'grid-vfx',      brands: ['Maxon','Autodesk'] },
      editing:  { file: 'out-editing.json',  grid: 'grid-editing',  brands: ['Adobe','Frame.io'] },
      hardware: { file: 'out-hardware.json', grid: 'grid-hardware', brands: ['TV Technology'] }
    };

    const segWrap = document.querySelector('.segmented');
    const chipsWrap = document.getElementById('brandChips');
    const loadBtn = document.getElementById('loadMoreBtn');

    let active = 'vfx';
    let store = { vfx:[], editing:[], hardware:[] };
    let filtered = [];     // current filtered list (active tab)
    let cursor = 0;        // index for load more
    const CHUNK = 9;       // 3 x 3 grid per click

    // Helpers
    const byId = (id) => document.getElementById(id);

    function setActiveTab(tab){
      // Switch tab button styles
      segWrap.querySelectorAll('.seg-btn').forEach(btn => {
        const on = btn.dataset.tab === tab;
        btn.classList.toggle('is-active', on);
        btn.setAttribute('aria-selected', on ? 'true' : 'false');
      });

      // Show the right grid, hide others
      Object.keys(TAB_CFG).forEach(key => {
        byId(TAB_CFG[key].grid).hidden = key !== tab;
      });

      // Build chips for this tab
      buildChips(tab);

      // Prepare data for this tab
      active = tab;
      ensureData(tab).then(() => {
        applyFiltersAndPaint(true);  // reset grid and paint first CHUNK
      });
    }

    function buildChips(tab){
      const brands = TAB_CFG[tab].brands;
      chipsWrap.innerHTML = '';
      brands.forEach(name => {
        const chip = document.createElement('button');
        chip.className = 'chip is-on';           // default ON (show all)
        chip.textContent = name;
        chip.dataset.brand = name;
        chip.addEventListener('click', () => {
          chip.classList.toggle('is-on');
          applyFiltersAndPaint(true);
        });
        chipsWrap.appendChild(chip);
      });
    }

    function getActiveBrands(){
      return [...chipsWrap.querySelectorAll('.chip.is-on')].map(c => c.dataset.brand);
    }

    function ensureData(tab){
      // If already loaded, return
      if (store[tab] && store[tab].length) return Promise.resolve();
      const file = TAB_CFG[tab].file;
      return fetch('data/' + file)
        .then(r => r.json())
        .then(items => { store[tab] = items || []; })
        .catch(()=>{ store[tab] = []; });
    }

    function applyFiltersAndPaint(reset){
      const brandsOn = getActiveBrands();
      const all = store[active] || [];

      // Filter by brand names against the "source" field
      filtered = brandsOn.length
        ? all.filter(it => brandsOn.some(b => (it.source || '').toLowerCase().includes(b.toLowerCase())))
        : all.slice();

      // Reset cursor and grid if needed
      if (reset) {
        cursor = 0;
        const grid = byId(TAB_CFG[active].grid);
        grid.innerHTML = '';
      }

      // Paint first/next chunk
      paintMore();
    }

    function paintMore(){
      const grid = byId(TAB_CFG[active].grid);
      const next = filtered.slice(cursor, cursor + CHUNK);
      next.forEach(item => grid.appendChild(renderCard(item)));
      cursor += next.length;

      // Button visibility
      if (cursor >= filtered.length) {
        loadBtn.style.display = 'none';
      } else {
        loadBtn.style.display = 'inline-block';
      }
    }

    // Wire segmented control
    segWrap.addEventListener('click', (e) => {
      const btn = e.target.closest('.seg-btn');
      if (!btn) return;
      const tab = btn.dataset.tab;
      if (tab && tab !== active) setActiveTab(tab);
    });

    // Load more handler
    loadBtn.addEventListener('click', () => paintMore());

    // Initial tab
    setActiveTab(active);
  };
})();
