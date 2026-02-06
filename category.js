/* =========================================================
   THE STREAMIC — Category Page Loader
   Loads items with "Load More" functionality
========================================================= */

(function() {
  /* ---------- Use Shared Card Renderer ---------- */
  const renderCard = window.__streamicRenderCard || ((item) => {
    const a = document.createElement('a');
    a.className = 'card';
    a.href = item.link || '#';
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    
    const fig = document.createElement('figure');
    fig.className = 'card-image';
    const img = document.createElement('img');
    img.alt = 'News image';
    img.loading = 'lazy';
    img.src = item.image || 'assets/fallback.jpg';
    img.addEventListener('error', () => { img.src = 'assets/fallback.jpg'; });
    fig.appendChild(img);
    a.appendChild(fig);
    
    const body = document.createElement('div');
    body.className = 'card-body';
    const h3 = document.createElement('h3');
    h3.textContent = item.title || 'Untitled';
    const source = document.createElement('span');
    source.className = 'source';
    source.textContent = item.source || '';
    body.appendChild(h3);
    body.appendChild(source);
    a.appendChild(body);
    
    return a;
  });
  
  /* ---------- Normalize Item ---------- */
  const normalize = (item) => ({
    title: item.title || item.headline || 'Untitled',
    link: item.link || item.url || '#',
    source: item.source || item.site || '',
    image: item.image || item.imageUrl || item.thumbnail || ''
  });
  
  /* ---------- Category to Feed Mapping ---------- */
  const FEED_MAP = {
    'streaming-tech': 'data/streaming-tech.json',
    'newsroom': 'data/newsroom.json',
    'playout': 'data/playout.json',
    'ip-video': 'data/ip-video.json',
    'cloud-ai': 'data/cloud-ai.json',
    'audio': 'data/audio.json'
  };
  
  /* ---------- Resolve Feed URL ---------- */
  function resolveFeedUrl(categoryKey) {
    // Handle both "streaming-tech" and "streaming-tech.json"
    const key = categoryKey.replace(/\.json$/i, '').toLowerCase();
    return FEED_MAP[key] || FEED_MAP['streaming-tech'];
  }
  
  /* ---------- Load Single Category Page ---------- */
  window.loadSingleCategory = function(categoryKey, options = {}) {
    const gridSelector = options.mount || '#content';
    const initialCount = options.first || 20;  // Show 20 initially (4 rows of 5)
    const loadMoreCount = options.step || 15;   // Load 15 more (3 rows of 5)
    
    const grid = document.querySelector(gridSelector);
    const feedUrl = resolveFeedUrl(categoryKey);
    
    if (!grid || !feedUrl) {
      console.error('Grid or feed URL not found');
      return;
    }
    
    let allItems = [];
    let currentIndex = 0;
    
    /* ---------- Render Function ---------- */
    function renderItems(count) {
      const slice = allItems.slice(currentIndex, currentIndex + count);
      slice.map(normalize).forEach(item => {
        grid.appendChild(renderCard(item));
      });
      currentIndex += slice.length;
      
      // Hide "Load More" button if all items are shown
      const loadMoreBtn = document.getElementById('loadMoreBtn');
      if (loadMoreBtn && currentIndex >= allItems.length) {
        loadMoreBtn.style.display = 'none';
      }
    }
    
    /* ---------- Fetch and Initialize ---------- */
    fetch(feedUrl)
      .then(response => response.json())
      .then(items => {
        if (!Array.isArray(items)) {
          console.error('Invalid data format');
          return;
        }
        
        allItems = items;
        renderItems(initialCount);
      })
      .catch(error => {
        console.error('Failed to load feed:', error);
        grid.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">Failed to load content. Please try again later.</p>';
      });
    
    /* ---------- Load More Button ---------- */
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', () => {
        renderItems(loadMoreCount);
      });
    }
  };
  
  /* ---------- Mobile Navigation ---------- */
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', !isExpanded);
      links.classList.toggle('active');
    });
  }
})();
