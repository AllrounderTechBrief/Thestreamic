/* =========================================================
   THE STREAMIC — Homepage Loader
   Loads 10 items per category section on the homepage
========================================================= */

(() => {
  /* ---------- Card Renderer ---------- */
  function renderCard(item) {
    const a = document.createElement('a');
    a.className = 'card';
    a.href = item.link || '#';
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    
    // Image
    const fig = document.createElement('figure');
    fig.className = 'card-image';
    const img = document.createElement('img');
    img.alt = item.source ? `Image from ${item.source}` : 'News image';
    img.loading = 'lazy';
    img.src = item.image || 'assets/fallback.jpg';
    img.addEventListener('error', () => { 
      img.src = 'assets/fallback.jpg'; 
    });
    fig.appendChild(img);
    a.appendChild(fig);
    
    // Body
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
    
    // Subtle hover effect
    a.addEventListener('pointermove', (e) => {
      const rect = a.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      const rotateX = Math.max(-3, Math.min(3, y * 3));
      const rotateY = Math.max(-3, Math.min(3, -x * 3));
      a.style.transform = `translateY(-4px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });
    
    a.addEventListener('pointerleave', () => {
      a.style.transform = '';
    });
    
    return a;
  }
  
  // Export for use in category pages
  window.__streamicRenderCard = renderCard;
  
  /* ---------- Normalize Item ---------- */
  const normalize = (item) => ({
    title: item.title || item.headline || 'Untitled',
    link: item.link || item.url || '#',
    source: item.source || item.site || '',
    image: item.image || item.imageUrl || item.thumbnail || ''
  });
  
  /* ---------- Category to JSON File Mapping ---------- */
  const FEED_MAP = {
    'streaming-tech': 'data/streaming-tech.json',
    'newsroom': 'data/newsroom.json',
    'playout': 'data/playout.json',
    'ip-video': 'data/ip-video.json',
    'cloud-ai': 'data/cloud-ai.json',
    'audio': 'data/audio.json'
  };
  
  /* ---------- Load Homepage Sections ---------- */
  function loadHomepage() {
    document.querySelectorAll('.home-section').forEach((section) => {
      const grid = section.querySelector('.card-grid');
      if (!grid || !grid.id) return;
      
      // Extract category from grid ID (e.g., "grid-streaming-tech" -> "streaming-tech")
      const categoryId = grid.id.replace('grid-', '');
      const feedUrl = FEED_MAP[categoryId];
      
      if (!feedUrl) {
        console.warn(`No feed mapping for category: ${categoryId}`);
        return;
      }
      
      // Fetch and render
      fetch(feedUrl)
        .then(response => response.json())
        .then(items => {
          if (!Array.isArray(items)) {
            console.error(`Invalid data format for ${feedUrl}`);
            return;
          }
          
          // Take first 10 items for homepage
          items.slice(0, 10).map(normalize).forEach(item => {
            grid.appendChild(renderCard(item));
          });
        })
        .catch(error => {
          console.error(`Failed to load ${feedUrl}:`, error);
        });
    });
  }
  
  /* ---------- Mobile Navigation Toggle ---------- */
  function initMobileNav() {
    const toggle = document.querySelector('.nav-toggle');
    const links = document.querySelector('.nav-links');
    
    if (toggle && links) {
      toggle.addEventListener('click', () => {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !isExpanded);
        links.classList.toggle('active');
      });
    }
  }
  
  /* ---------- Initialize ---------- */
  if (document.querySelector('.home')) {
    if (document.readyState !== 'loading') {
      loadHomepage();
      initMobileNav();
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        loadHomepage();
        initMobileNav();
      });
    }
  }
})();
