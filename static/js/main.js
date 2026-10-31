/**
 * The Chronicle — Core Frontend Interactions
 * Handles Dark/Light mode, breaking ticker, search modal,
 * reading progress bar, font sizing, and mobile navigation.
 */

(function () {
  'use strict';

  // 1. Dark Mode System
  const themeToggleBtns = document.querySelectorAll('.theme-toggle');

  function updateThemeIcons(isDark) {
    document.querySelectorAll('.theme-icon-sun').forEach(el => {
      el.classList.toggle('hidden', !isDark);
    });
    document.querySelectorAll('.theme-icon-moon').forEach(el => {
      el.classList.toggle('hidden', isDark);
    });
  }

  function setTheme(theme) {
    document.documentElement.classList.add('theme-transition');
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      updateThemeIcons(true);
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      updateThemeIcons(false);
    }
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transition');
    }, 300);
  }

  // Initialize icon state
  const isCurrentlyDark = document.documentElement.classList.contains('dark');
  updateThemeIcons(isCurrentlyDark);

  themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.contains('dark');
      setTheme(isDark ? 'light' : 'dark');
    });
  });

  // Listen to OS preference change if no explicit storage is set
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });

  // 2. Mobile Navigation Drawer
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenuDrawer = document.getElementById('mobile-menu-drawer');
  const mobileMenuClose = document.getElementById('mobile-menu-close');
  const mobileMenuBackdrop = document.getElementById('mobile-menu-backdrop');

  if (mobileMenuBtn && mobileMenuDrawer) {
    const openMenu = () => {
      mobileMenuDrawer.classList.remove('translate-x-full');
      mobileMenuDrawer.classList.add('translate-x-0');
      if (mobileMenuBackdrop) mobileMenuBackdrop.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
    };

    const closeMenu = () => {
      mobileMenuDrawer.classList.add('translate-x-full');
      mobileMenuDrawer.classList.remove('translate-x-0');
      if (mobileMenuBackdrop) mobileMenuBackdrop.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    };

    mobileMenuBtn.addEventListener('click', openMenu);
    if (mobileMenuClose) mobileMenuClose.addEventListener('click', closeMenu);
    if (mobileMenuBackdrop) mobileMenuBackdrop.addEventListener('click', closeMenu);
  }

  // 3. Search Modal & Keyboard Shortcut (Cmd+K / Ctrl+K)
  const searchModal = document.getElementById('search-modal');
  const openSearchBtns = document.querySelectorAll('.open-search-modal');
  const closeSearchBtn = document.getElementById('close-search-modal');
  const searchInput = document.getElementById('modal-search-input');

  function openSearch() {
    if (!searchModal) return;
    searchModal.classList.remove('hidden');
    searchModal.classList.add('flex');
    document.body.classList.add('overflow-hidden');
    setTimeout(() => {
      if (searchInput) searchInput.focus();
    }, 50);
  }

  function closeSearch() {
    if (!searchModal) return;
    searchModal.classList.add('hidden');
    searchModal.classList.remove('flex');
    document.body.classList.remove('overflow-hidden');
  }

  openSearchBtns.forEach(btn => btn.addEventListener('click', openSearch));
  if (closeSearchBtn) closeSearchBtn.addEventListener('click', closeSearch);

  if (searchModal) {
    searchModal.addEventListener('click', (e) => {
      if (e.target === searchModal) closeSearch();
    });
  }

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      if (searchModal && !searchModal.classList.contains('hidden')) {
        closeSearch();
      } else {
        openSearch();
      }
    }
    if (e.key === 'Escape' && searchModal && !searchModal.classList.contains('hidden')) {
      closeSearch();
    }
  });

  // 4. Breaking News Ticker Carousel
  const tickerItems = document.querySelectorAll('.ticker-item');
  const prevTickerBtn = document.getElementById('ticker-prev');
  const nextTickerBtn = document.getElementById('ticker-next');
  let currentTickerIdx = 0;
  let tickerInterval = null;

  function showTickerItem(index) {
    if (!tickerItems.length) return;
    tickerItems.forEach((el, idx) => {
      el.classList.toggle('hidden', idx !== index);
    });
    currentTickerIdx = index;
  }

  function nextTicker() {
    if (!tickerItems.length) return;
    const nextIdx = (currentTickerIdx + 1) % tickerItems.length;
    showTickerItem(nextIdx);
  }

  function prevTicker() {
    if (!tickerItems.length) return;
    const prevIdx = (currentTickerIdx - 1 + tickerItems.length) % tickerItems.length;
    showTickerItem(prevIdx);
  }

  function startTicker() {
    if (tickerItems.length > 1) {
      tickerInterval = setInterval(nextTicker, 5000);
    }
  }

  function pauseTicker() {
    if (tickerInterval) clearInterval(tickerInterval);
  }

  if (tickerItems.length > 0) {
    showTickerItem(0);
    startTicker();

    const tickerContainer = document.getElementById('breaking-news-bar');
    if (tickerContainer) {
      tickerContainer.addEventListener('mouseenter', pauseTicker);
      tickerContainer.addEventListener('mouseleave', startTicker);
    }
    if (prevTickerBtn) prevTickerBtn.addEventListener('click', prevTicker);
    if (nextTickerBtn) nextTickerBtn.addEventListener('click', nextTicker);
  }

  // 5. Article Reading Progress Bar
  const progressBar = document.getElementById('reading-progress');
  const articleBody = document.querySelector('.article-body');

  if (progressBar && articleBody) {
    window.addEventListener('scroll', () => {
      const articleRect = articleBody.getBoundingClientRect();
      const articleHeight = articleBody.offsetHeight;
      const windowHeight = window.innerHeight;
      const scrolled = windowHeight - articleRect.top;

      let progress = (scrolled / articleHeight) * 100;
      progress = Math.min(Math.max(progress, 0), 100);
      progressBar.style.width = `${progress}%`;
    }, { passive: true });
  }

  // 6. Article Font Resizer (A- / A+)
  const fontSizeBtns = document.querySelectorAll('.font-size-btn');
  if (fontSizeBtns.length && articleBody) {
    const fontSizes = ['text-base', 'text-lg', 'text-xl'];
    let currentSizeIdx = 1; // default 'text-lg'

    fontSizeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        if (action === 'increase' && currentSizeIdx < fontSizes.length - 1) {
          currentSizeIdx++;
        } else if (action === 'decrease' && currentSizeIdx > 0) {
          currentSizeIdx--;
        }

        fontSizes.forEach(cls => articleBody.classList.remove(cls));
        articleBody.classList.add(fontSizes[currentSizeIdx]);
      });
    });
  }

  // 7. Share / Copy Link Feedback
  const copyLinkBtns = document.querySelectorAll('.copy-link-btn');
  copyLinkBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navigator.clipboard.writeText(window.location.href).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = `<span class="text-xs text-emerald-500 font-medium">Copied!</span>`;
        setTimeout(() => {
          btn.innerHTML = originalText;
        }, 2000);
      });
    });
  });

  // 8. Back to Top Button
  const backToTopBtn = document.getElementById('back-to-top');
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 400) {
        backToTopBtn.classList.remove('opacity-0', 'pointer-events-none');
        backToTopBtn.classList.add('opacity-100');
      } else {
        backToTopBtn.classList.add('opacity-0', 'pointer-events-none');
        backToTopBtn.classList.remove('opacity-100');
      }
    }, { passive: true });

    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

})();
