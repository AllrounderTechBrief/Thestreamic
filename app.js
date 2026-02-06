/* =========================================================
   STREAMIC — App bootstrap (home loader + UX basics)
   - Mobile nav toggle
   - Cookie bar
   - Card renderer (preload + fade-in)
   - Home sections loader (.home-section[data-json])
   - Hooks into StreamicVisuals for effects
   ========================================================= */

(() => {
  /* -------------------- Mobile nav toggle -------------------- */
  const toggle = document.querySelector('.nav-toggle');
  const links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const exp = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!exp));
      links.classList.toggle('show');
    });
  }

  /* -------------------- Cookie bar -------------------- */
  const bar = document.getElementById('cookieBar');
  if (bar) {
    try { if (!localStorage.getItem('cookieChoice')) { bar.hidden = false; } }
    catch (e) { bar.hidden = false; }

    const hide = (choice) => {
      try { localStorage.setItem('cookieChoice', choice); } catch (e) {}
      bar.classList.add('is-hidden'); bar.hidden = true;
      setTimeout(() => { bar.parentNode && bar.parentNode.removeChild(bar); }, 300);
    };
    const acc = document.getElementById('cookieAccept');
    const ess = document.getElementById('cookieEssential');
    if (acc) acc.onclick = () => hide('all');
    if (ess) ess.onclick = () => hide('essential');
  }

  /* -------------------- Card factory -------------------- */
  function renderCard(item) {
    const a = document.createElement('a');
    a.className = 'card';
    a.href = item.link;
    a.target = '_blank';
    a.rel = 'noopener';

    // Image wrapper
    const w = document.createElement('div');
    w.className = 'card-image';

    const img = document.createElement('img');
    img.alt = item.source ? ('Image from ' + item.source) : 'News image';
    img.src = 'assets/fallback.jpg';
    img.loading = 'lazy';

    // Progressive image load (no blur; CSS will fade opacity via .loaded)
    if (item.image) {
      const pre = new Image();
      pre.onload = () => { img.src = item.image; img.classList.add('loaded'); };
      pre.src = item.image;
    } else {
      requestAnimationFrame(() => img.classList.add('loaded'));
    }

    w.appendChild(img);
    a.appendChild(w);

    // Body
    const b = document.createElement('div');
    b.className = 'card-body';
    const h = document.createElement('h3');
    h.textContent = item.title || 'Untitled';
    const s = document.createElement('span');
    s.className = 'source';
    s.textContent = item.source || '';
    b.appendChild(h);
    b.appendChild(s);
    a.appendChild(b);

    // Visual hooks (fade-in, parallax, tilt)
    const binder = window.StreamicVisuals?.attach || window.__streamicBindCardEnhancements;
    if (typeof binder === 'function') binder(a);

    return a;
  }

  // Expose for category.js if it wants to reuse
  window.__streamicRenderCard = renderCard;

  /* -------------------- Home loader (.home-section) -------------------- */
  function loadHome() {
    document.querySelectorAll('.home-section').forEach((sec) => {
      const file = sec.getAttribute('data-json');
      const grid = sec.querySelector('.card-grid');
      if (!file || !grid) return;

      fetch('data/' + file)
        .then((r) => r.json())
        .then((items) => {
          (items || []).slice(0, 10).forEach((it) => grid.appendChild(renderCard(it)));
          // trigger a parallax update pass if visual system exists
          if (window.StreamicVisuals) {
            // just poke reflow for parallax vars next frame
            requestAnimationFrame(() => window.dispatchEvent(new Event('scroll')));
          }
        })
        .catch(() => { /* fail silently */ });
    });
  }

  if (document.querySelector('.home')) {
    if (document.readyState !== 'loading') loadHome();
    else document.addEventListener('DOMContentLoaded', loadHome);
  }
})();
