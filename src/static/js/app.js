(() => {
  const sidebar = document.querySelector('#sidebar');
  const toggle = document.querySelector('.menu-button');
  const backdrop = document.querySelector('.backdrop');
  const mobile = matchMedia('(max-width: 760px)');
  function setMenu(open) {
    if (!sidebar) return;
    sidebar.classList.toggle('open', open);
    sidebar.inert = mobile.matches && !open;
    if (sidebar.inert) sidebar.setAttribute('aria-hidden', 'true');
    else sidebar.removeAttribute('aria-hidden');
    toggle?.setAttribute('aria-expanded', String(open));
    if (backdrop) backdrop.hidden = !open;
  }
  toggle?.addEventListener('click', () => setMenu(!sidebar.classList.contains('open')));
  backdrop?.addEventListener('click', () => { setMenu(false); toggle?.focus(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { setMenu(false); if (mobile.matches) toggle?.focus(); }
  });
  mobile.addEventListener('change', () => setMenu(false));
  setMenu(false);
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
})();
