// category.js (FINAL)
// Use: loadSingleCategory('<page-key>') where key ∈
//   streaming-tech | newsroom | playout | ip-video | cloud-ai | audio
// These keys map to the 3 JSON outputs from build.py.

(function(){
  const renderCard = window.__streamicRenderCard || ((i) => {
    const a = document.createElement('a');
    a.className = 'card'; a.href = i.link || '#'; a.target = '_blank'; a.rel = 'noopener';
    const fig = document.createElement('figure'); fig.className = 'card-image';
    const img = document.createElement('img'); img.alt = 'News image'; img.loading = 'lazy'; img.src = i.image || 'assets/fallback.jpg';
    img.addEventListener('error', () => { img.src = 'assets/fallback.jpg'; });
    fig.appendChild(img); a.appendChild(fig);
    const b = document.createElement('div'); b.className = 'card-body';
    const h = document.createElement('h3'); h.textContent = i.title || 'Untitled';
    const s = document.createElement('span'); s.className = 'source'; s.textContent = i.source || '';
    b.appendChild(h); b.appendChild(s); a.appendChild(b);
    return a;
  });

  const norm = (it) => ({
    title:  it.title || it.headline || 'Untitled',
    link:   it.link || it.url || '#',
    source: it.source || it.site || '',
    image:  it.image || it.imageUrl || it.thumbnail || ''
  });

  // Single source map—keeps build.py unchanged
  const SOURCE_MAP = {
    'streaming-tech': 'data/out-hardware.json',
    'newsroom':       'data/out-editing.json',
    'playout':        'data/out-hardware.json',
    'ip-video':       'data/out-3d-vfx.json',
    'cloud-ai':       'data/out-editing.json',
    'audio':          'data/out-hardware.json'
  };

  window.loadSingleCategory = function(pageKey, options = {}){
    const gridSel = options.mount || '#content';
    const first = options.first || 18;
    const step  = options.step  || 12;

    const grid = document.querySelector(gridSel);
    const src  = SOURCE_MAP[pageKey];
    if (!grid || !src) return;

    let items = [], idx = 0;

    function paint(count){
      const slice = items.slice(idx, idx + count);
      slice.map(norm).forEach((it) => grid.appendChild(renderCard(it)));
      idx += slice.length;

      const btn = document.getElementById('loadMoreBtn');
      if (btn && idx >= items.length) btn.style.display = 'none';
    }

    fetch(src)
      .then(r => r.json())
      .then(list => { items = Array.isArray(list) ? list : (list.items || []); paint(first); })
      .catch(() => { /* leave empty gracefully */ });

    const btn = document.getElementById('loadMoreBtn');
    if (btn) btn.onclick = () => paint(step);
  };
})();
