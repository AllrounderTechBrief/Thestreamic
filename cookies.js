/* =========================================================
   THE STREAMIC — Cookie Consent Manager
========================================================= */

(function() {
  const COOKIE_CONSENT_KEY = 'streamic_cookie_consent';
  
  /* ---------- Check if consent already given ---------- */
  function hasConsent() {
    return localStorage.getItem(COOKIE_CONSENT_KEY) !== null;
  }
  
  /* ---------- Save consent ---------- */
  function saveConsent(accepted) {
    localStorage.setItem(COOKIE_CONSENT_KEY, accepted ? 'accepted' : 'rejected');
    hideConsentBanner();
  }
  
  /* ---------- Hide banner ---------- */
  function hideConsentBanner() {
    const banner = document.querySelector('.cookie-consent');
    if (banner) {
      banner.classList.remove('show');
      setTimeout(() => banner.remove(), 300);
    }
  }
  
  /* ---------- Show banner ---------- */
  function showConsentBanner() {
    if (hasConsent()) return;
    
    const banner = document.createElement('div');
    banner.className = 'cookie-consent';
    banner.innerHTML = `
      <div class="cookie-consent-inner">
        <p>
          We use cookies to improve your browsing experience. 
          By continuing to use this site, you agree to our 
          <a href="cookies.html">Cookie Policy</a> and 
          <a href="privacy.html">Privacy Policy</a>.
        </p>
        <div class="cookie-buttons">
          <button class="cookie-btn reject" id="rejectCookies">Reject</button>
          <button class="cookie-btn accept" id="acceptCookies">Accept</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    
    // Show with animation
    setTimeout(() => banner.classList.add('show'), 100);
    
    // Event listeners
    document.getElementById('acceptCookies').addEventListener('click', () => {
      saveConsent(true);
    });
    
    document.getElementById('rejectCookies').addEventListener('click', () => {
      saveConsent(false);
    });
  }
  
  /* ---------- Initialize ---------- */
  if (document.readyState !== 'loading') {
    showConsentBanner();
  } else {
    document.addEventListener('DOMContentLoaded', showConsentBanner);
  }
})();
