(() => {
  const initial = document.querySelector('#dashboard-initial');
  if (!initial) return;
  const currency = value => new Intl.NumberFormat('vi-VN', {maximumFractionDigits: 0}).format(value) + ' ₫';
  const node = (tag, text, cls) => {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  };
  function chart(data) {
    const host = document.querySelector('#revenue-chart');
    host.replaceChildren();
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const width = Math.max(host.clientWidth, 260);
    const left = 50, right = width - 14;
    svg.setAttribute('viewBox', `0 0 ${width} 235`);
    svg.setAttribute('preserveAspectRatio', 'none');
    const max = Math.max(...data.map(d => d.revenue), 1);
    const min = Math.min(...data.map(d => d.revenue), 0);
    const y = value => 190 - ((value - min) / (max - min)) * 160;
    const x = index => data.length === 1 ? (left + right) / 2 : left + index * ((right - left) / (data.length - 1));
    const el = (tag, attrs, text) => {
      const e = document.createElementNS(svg.namespaceURI, tag);
      Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
      if (text !== undefined) e.textContent = text;
      svg.append(e); return e;
    };
    for (let i = 0; i <= 4; i++) {
      const value = min + (max - min) * i / 4;
      const label = Math.abs(value) >= 1e6 ? (value / 1e6).toFixed(1) + 'tr' : Math.abs(value) >= 1000 ? (value / 1000).toFixed(0) + 'k' : value.toFixed(0);
      el('line', {x1: left, x2: right, y1: y(value), y2: y(value), stroke: '#e8ece3', 'stroke-dasharray': '3 4'});
      el('text', {x: left - 8, y: y(value) + 3, 'text-anchor': 'end', fill: '#91998c', 'font-size': 10}, label);
    }
    const points = data.map((d, i) => `${x(i)},${y(d.revenue)}`).join(' ');
    el('polygon', {points: `${x(0)},${y(0)} ${points} ${x(data.length - 1)},${y(0)}`, fill: '#e9f1da', opacity: 0.7});
    el('polyline', {points, fill: 'none', stroke: '#7ca25c', 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'vector-effect': 'non-scaling-stroke'});
    data.forEach((d, i) => {
      if (i % Math.max(1, Math.ceil(data.length / (width < 450 ? 3 : 7))) === 0 || i === data.length - 1) {
        el('text', {x: x(i), y: 220, 'text-anchor': 'middle', fill: '#91998c', 'font-size': 10}, d.label);
      }
      if (data.length < 40) {
        const circle = el('circle', {cx: x(i), cy: y(d.revenue), r: 3, fill: '#648d46'});
        const title = document.createElementNS(svg.namespaceURI, 'title');
        title.textContent = `${d.date}: ${currency(d.revenue)}`; circle.append(title);
      }
    });
    host.append(svg);
  }
  let currentData;
  function render(data) {
    currentData = data;
    ['revenue', 'profit', 'stock_value', 'collected', 'refunds', 'orders', 'returns', 'stock_units', 'low_count'].forEach(key => {
      const target = document.querySelector('#metric-' + key);
      if (target) target.textContent = ['orders', 'returns', 'stock_units', 'low_count'].includes(key) ? data[key] : currency(data[key]);
    });
    chart(data.daily);
    const table = document.querySelector('#daily-table'); table.replaceChildren();
    data.daily.forEach(d => { const row = node('tr'); row.append(node('td', d.date), node('td', currency(d.revenue), 'numeric')); table.append(row); });
    const top = document.querySelector('#top-products'); top.replaceChildren();
    const max = Math.max(...data.top.map(d => d.units), 1);
    data.top.forEach(d => {
      const item = node('div', undefined, 'ranking-item'); const label = node('div', undefined, 'ranking-label');
      label.append(node('span', d.name), node('strong', d.units));
      const track = node('div', undefined, 'ranking-bar'); const bar = node('span'); bar.style.width = `${d.units / max * 100}%`; track.append(bar);
      item.append(label, track); top.append(item);
    });
    if (!data.top.length) top.append(node('p', 'Chưa có sản phẩm bán trong kỳ.', 'empty'));
    const recent = document.querySelector('#recent-sales'); recent.replaceChildren();
    data.recent.forEach(d => {
      const row = node('tr'); const cell = node('td'); const link = node('a', d.code, 'text-link'); link.href = `/document/${d.id}/`;
      cell.append(link, node('small', d.customer)); row.append(cell, node('td', currency(d.total), 'numeric'), node('td', d.status)); recent.append(row);
    });
    if (!data.recent.length) { const row = node('tr'); const cell = node('td', 'Chưa có đơn bán trong kỳ.', 'empty'); cell.colSpan = 3; row.append(cell); recent.append(row); }
    const low = document.querySelector('#low-stock'); low.replaceChildren();
    data.low_stock.forEach(d => { const item = node('div', undefined, 'low-stock-item'); const label = node('div'); label.append(node('span', d.name), node('small', `${d.sku} · Ngưỡng ${d.threshold}`)); item.append(label, node('strong', d.quantity)); low.append(item); });
    if (!data.low_stock.length) low.append(node('p', 'Không có sản phẩm tồn thấp.', 'empty'));
    document.querySelector('#refresh-status').textContent = `Cập nhật ${data.updated_at} · Tự làm mới mỗi 10 giây`;
  }
  render(JSON.parse(initial.textContent));
  let inFlight = false;
  async function refresh() {
    if (inFlight || document.hidden) return;
    inFlight = true;
    try {
      const response = await fetch('/dashboard/data/' + location.search, {headers: {'Accept': 'application/json'}, signal: AbortSignal.timeout(8000), cache: 'no-store'});
      if (!response.ok || response.redirected) throw new Error('Không thể tải dữ liệu');
      render(await response.json());
    } catch (_) {
      document.querySelector('#refresh-status').textContent = 'Chưa thể cập nhật · Đang giữ dữ liệu cũ, sẽ thử lại sau 10 giây';
    } finally { inFlight = false; }
  }
  let resizeQueued = false;
  window.addEventListener('resize', () => {
    if (resizeQueued) return;
    resizeQueued = true;
    requestAnimationFrame(() => { chart(currentData.daily); resizeQueued = false; });
  });
  setInterval(refresh, 10000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
})();
