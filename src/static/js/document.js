(() => {
  const form = document.querySelector('.document-form');
  if (!form) return;
  const count = document.querySelector('#id_lines-TOTAL_FORMS');
  const rows = document.querySelector('#line-rows');
  const addButton = document.querySelector('#add-line');
  const undoButton = document.querySelector('#undo-line');
  const status = document.querySelector('#line-status');
  const empty = document.querySelector('#line-empty');
  let lastRemoved = null;

  const activeRows = () => [...rows.querySelectorAll('.line-row')].filter(row => !row.hidden);
  const deletionInput = row => row.querySelector('[name$="-DELETE"]');

  function updateState(message) {
    const visible = activeRows();
    addButton.disabled = visible.length >= 100;
    empty.hidden = visible.length > 0;
    undoButton.hidden = !lastRemoved;
    visible.forEach((row, index) => {
      row.querySelector('[data-remove-line]').setAttribute('aria-label', `Xóa dòng ${index + 1}`);
    });
    if (message) status.textContent = message;
  }

  function markRemoved(row, removed) {
    const checkbox = deletionInput(row);
    checkbox.value = removed ? 'True' : '';
    row.hidden = removed;
    row.querySelectorAll('input, select, textarea').forEach(control => {
      if (control !== checkbox) control.disabled = removed;
    });
  }

  function prepareRow(row) {
    const checkbox = deletionInput(row);
    if (form.dataset.kind === 'sale') {
      row.classList.add('sale');
      const price = row.querySelector('[name$="unit_price"]');
      price.closest('.field').hidden = true;
      price.required = false;
    }
    if (['true', 'on', '1'].includes(checkbox.value.toLowerCase())) markRemoved(row, true);
  }

  rows.addEventListener('click', event => {
    const button = event.target.closest('[data-remove-line]');
    if (!button) return;
    const row = button.closest('.line-row');
    const position = activeRows().indexOf(row);
    markRemoved(row, true);
    lastRemoved = row;
    updateState('Đã xóa dòng sản phẩm. Bạn có thể hoàn tác trước khi lưu.');
    const nextRow = activeRows()[Math.min(position, activeRows().length - 1)];
    (nextRow?.querySelector('[data-remove-line]') || addButton).focus();
  });

  undoButton.addEventListener('click', () => {
    if (!lastRemoved) return;
    const row = lastRemoved;
    markRemoved(row, false);
    lastRemoved = null;
    updateState('Đã khôi phục dòng sản phẩm.');
    row.querySelector('select').focus();
  });

  addButton.addEventListener('click', () => {
    if (activeRows().length >= 100) return;
    const reusable = [...rows.querySelectorAll('.line-row')].find(row => row.hidden);
    const index = reusable ? deletionInput(reusable).name.match(/-(\d+)-DELETE$/)[1] : count.value;
    const template = document.createElement('template');
    template.innerHTML = document.querySelector('#empty-line').innerHTML.replaceAll('__prefix__', index);
    const row = template.content.firstElementChild;
    prepareRow(row);
    if (reusable) reusable.replaceWith(row);
    else { rows.append(row); count.value = Number(count.value) + 1; }
    lastRemoved = null;
    updateState('Đã thêm dòng sản phẩm.');
    row.querySelector('select').focus();
  });

  rows.querySelectorAll('.line-row').forEach(prepareRow);
  updateState();
})();
