const menuToggle = document.querySelector('[data-menu-toggle]');
const nav = document.querySelector('[data-nav]');

if (menuToggle && nav) {
  const closeMenu = () => {
    menuToggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    document.body.classList.remove('nav-open');
  };

  menuToggle.addEventListener('click', () => {
    const opening = menuToggle.getAttribute('aria-expanded') !== 'true';
    menuToggle.setAttribute('aria-expanded', String(opening));
    nav.classList.toggle('is-open', opening);
    document.body.classList.toggle('nav-open', opening);
  });

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  window.addEventListener('resize', () => {
    if (window.innerWidth > 900) closeMenu();
  });
}

document.querySelectorAll('[data-year]').forEach((node) => {
  node.textContent = new Date().getFullYear();
});

const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px' });
  reveals.forEach((node) => observer.observe(node));
} else {
  reveals.forEach((node) => node.classList.add('is-visible'));
}
