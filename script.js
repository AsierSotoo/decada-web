(() => {
  'use strict';
  if (!location.hash) window.scrollTo({top: 0, left: 0, behavior: 'instant'});
  window.addEventListener('pageshow', () => { if (!location.hash) window.scrollTo({top: 0, left: 0, behavior: 'instant'}); });
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const root = new URL('.', document.currentScript.src);
  const url = path => new URL(path, root).href;
  const money = amount => new Intl.NumberFormat('es-ES', {style:'currency', currency:'EUR'}).format(amount);
  const normalize = text => text.toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const skip = document.createElement('a');
  skip.className = 'skip-link'; skip.href = '#contenido'; skip.textContent = 'Saltar al contenido'; document.body.prepend(skip);

  const heroEntranceEl = $('.hero.entrance');
  if (document.documentElement.classList.contains('intro-run')) {
    const splash = $('#intro-splash');
    if (!splash) {
      document.documentElement.classList.remove('intro-run');
      if (heroEntranceEl) requestAnimationFrame(() => heroEntranceEl.classList.add('run'));
    }
    else {
      const heroEntrance = heroEntranceEl;
      let done = false;
      const reveal = () => {
        splash.classList.add('is-out');
        document.documentElement.classList.remove('intro-run');
        if (heroEntrance) requestAnimationFrame(() => heroEntrance.classList.add('run'));
        setTimeout(() => splash.remove(), 750);
      };
      const finish = () => {
        if (done) return; done = true;
        try { sessionStorage.setItem('decadaIntro', '1'); } catch (e) {}
        reveal();
      };
      if (reduced.matches) { finish(); }
      else if (splash.classList.contains('intro-name')) {
        const stage = $('.name-stage', splash), kicker = $('.name-kicker', splash), mask = $('.name-mask', splash), stitch = $('.name-stitch', splash), cap = $('.name-cap', splash), pct = $('#intro-pct', splash), sprkL = $('#intro-sprk-l', splash), sprkR = $('#intro-sprk-r', splash), rec = $('#intro-rec', splash), tc = $('#intro-tc', splash), stamp = $('#intro-stamp', splash);
        setTimeout(() => { stage.classList.add('show'); kicker.classList.add('show'); rec.classList.add('show'); }, 80);
        setTimeout(() => { mask.classList.add('run'); stitch.classList.add('run'); cap.classList.add('show'); sprkL.classList.add('show'); sprkR.classList.add('show'); }, 380);
        const dur = 2300, start = performance.now() + 380;
        const tcStart = performance.now();
        let tcTimer = setInterval(() => {
          if (done) { clearInterval(tcTimer); return; }
          const s = Math.min(9, Math.round((performance.now() - tcStart) / 1000));
          if (tc) tc.textContent = '00:0' + s;
        }, 250);
        const frame = now => {
          if (done) return;
          const t = Math.max(0, Math.min(1, (now - start) / dur));
          if (pct) pct.textContent = String(Math.round(t * 100)).padStart(2, '0');
          if (t < 1) requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
        setTimeout(() => stamp.classList.add('show'), 380 + 2300 + 120);
        setTimeout(finish, 380 + 2300 + 900);
      } else {
        const wrap = $('.tag-wrap', splash), card = $('.tag-card', splash);
        setTimeout(() => wrap.classList.add('show'), 150);
        setTimeout(() => card.classList.add('flip'), 1650);
        setTimeout(() => wrap.classList.add('is-leaving'), 3300);
        setTimeout(finish, 3550);
      }
      splash.addEventListener('click', finish);
      window.addEventListener('keydown', finish, {once: true});
    }
  } else if (heroEntranceEl) {
    requestAnimationFrame(() => heroEntranceEl.classList.add('run'));
  }
  let noticeTimer;
  const notice = text => {
    let node = $('.notice');
    if (!node) { node = document.createElement('div'); node.className = 'notice'; node.setAttribute('role','status'); document.body.append(node); }
    node.textContent = text; node.hidden = false;
    clearTimeout(noticeTimer); noticeTimer = setTimeout(() => node.hidden = true, 4200);
  };
  const menu = $('.menu-button'), nav = $('#nav');
  const setMenu = open => { menu.setAttribute('aria-expanded', String(open)); menu.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú'); nav.classList.toggle('open', open); document.body.classList.toggle('nav-open', open); };
  menu?.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  nav?.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav?.classList.contains('open')) { setMenu(false); menu.focus(); } });
  document.addEventListener('click', e => { if (nav?.classList.contains('open') && !e.target.closest('.site-header')) setMenu(false); });
  const locationPath = location.pathname.replace(/index\.html$/, '').replace(/\/$/, '');
  $$('.main-nav > a').forEach(a => { if (new URL(a.href).pathname.replace(/index\.html$/, '').replace(/\/$/, '') === locationPath) a.setAttribute('aria-current','page'); });

  const hero = $('[data-hero-slideshow]');
  if (hero) {
    const slides = $$('.hero-slide', hero), dots = $$('.hero-slide-controls button', hero);
    let current = 0, timer, paused = false;
    const show = index => {
      current = index;
      slides.forEach((slide, i) => { slide.classList.toggle('is-active', i === index); slide.setAttribute('aria-hidden', String(i !== index)); });
      dots.forEach((dot, i) => { dot.classList.toggle('is-active', i === index); dot.setAttribute('aria-current', i === index ? 'true' : 'false'); });
    };
    const stop = () => { clearInterval(timer); timer = null; };
    const play = () => { if (!timer && !paused && !reduced.matches && !document.hidden) timer = setInterval(() => show((current + 1) % slides.length), 7000); };
    dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); stop(); play(); }));
    hero.addEventListener('mouseenter', stop); hero.addEventListener('mouseleave', play);
    hero.addEventListener('focusin', stop); hero.addEventListener('focusout', play);
    document.addEventListener('visibilitychange', () => document.hidden ? stop() : play()); reduced.addEventListener('change', () => reduced.matches ? stop() : play());
    show(0); play();
  }
  $$('[data-product-gallery]').forEach(gallery => {
    const main = $('[data-gallery-main]', gallery), dialog = $('dialog', gallery), enlarged = $('[data-lightbox-image]', gallery);
    const stage = $('.product-gallery-stage', gallery), thumbs = $$('[data-gallery-src]', gallery), lbStage = $('.lb-stage', dialog);
    const counter = $('.gallery-count', dialog), strip = $('[data-lb-thumbs]', dialog);
    let current = 0;
    const pad = n => String(n).padStart(2, '0');
    const unzoom = () => { lbStage.classList.remove('is-zoomed'); enlarged.style.transformOrigin = ''; };
    const lbThumbs = thumbs.map((thumb, i) => {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'lb-thumb'; b.setAttribute('aria-label', `Fotografía ${i + 1}`);
      const img = document.createElement('img'); img.src = thumb.dataset.gallerySrc; img.alt = ''; b.append(img); b.addEventListener('click', () => choose(i)); strip?.append(b); return b;
    });
    if (thumbs.length < 2) strip?.remove();
    const choose = index => {
      current = (index + thumbs.length) % thumbs.length; unzoom();
      const thumb = thumbs[current]; if (thumb.dataset.gallerySrcset) { main.srcset = thumb.dataset.gallerySrcset; } else { main.removeAttribute('srcset'); } main.src = enlarged.src = thumb.dataset.gallerySrc; main.alt = enlarged.alt = thumb.dataset.galleryAlt;
      counter.textContent = `${pad(current + 1)} / ${pad(thumbs.length)}`;
      thumbs.forEach((button, i) => { button.classList.toggle('is-active', i === current); button.setAttribute('aria-pressed', String(i === current)); });
      lbThumbs.forEach((button, i) => { button.classList.toggle('is-active', i === current); button.setAttribute('aria-current', i === current ? 'true' : 'false'); });
    };
    thumbs.forEach((thumb, i) => thumb.addEventListener('click', () => choose(i)));
    if (thumbs.length > 1) [-1, 1].forEach(direction => {
      const button = document.createElement('button'); button.type = 'button'; button.className = `gallery-nav ${direction < 0 ? 'prev' : 'next'}`;
      button.setAttribute('aria-label', direction < 0 ? 'Fotografía anterior' : 'Fotografía siguiente');
      button.innerHTML = direction < 0 ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>' : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>';
      button.addEventListener('click', () => choose(current + direction)); lbStage.append(button);
    });
    let startX = null, swiped = false;
    stage.addEventListener('pointerdown', e => { startX = e.clientX; swiped = false; });
    stage.addEventListener('pointerup', e => { if (startX === null || thumbs.length < 2) return; const dx = e.clientX - startX; startX = null; if (Math.abs(dx) > 40) { swiped = true; choose(current + (dx < 0 ? 1 : -1)); } });
    stage.addEventListener('click', e => { if (swiped) { swiped = false; e.preventDefault(); return; } dialog.showModal(); document.documentElement.classList.add('lb-open'); });
    let lbStart = null;
    lbStage.addEventListener('pointerdown', e => { lbStart = e.clientX; });
    lbStage.addEventListener('pointerup', e => { if (lbStart === null) return; const dx = e.clientX - lbStart; lbStart = null; if (e.pointerType !== 'mouse' && Math.abs(dx) > 40 && thumbs.length > 1 && !lbStage.classList.contains('is-zoomed')) choose(current + (dx < 0 ? 1 : -1)); });
    const origin = e => { const r = enlarged.getBoundingClientRect(); enlarged.style.transformOrigin = `${(e.clientX - r.left) / r.width * 100}% ${(e.clientY - r.top) / r.height * 100}%`; };
    enlarged.addEventListener('click', e => { e.stopPropagation(); const on = !lbStage.classList.contains('is-zoomed'); lbStage.classList.toggle('is-zoomed', on); if (on) origin(e); else enlarged.style.transformOrigin = ''; });
    enlarged.addEventListener('mousemove', e => { if (lbStage.classList.contains('is-zoomed')) origin(e); });
    lbStage.addEventListener('click', e => { if (e.target === lbStage) dialog.close(); });
    $('.lightbox-close', dialog).addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => { unzoom(); document.documentElement.classList.remove('lb-open'); stage.focus(); });
    dialog.addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); choose(current + (e.key === 'ArrowRight' ? 1 : -1)); } }); choose(0);
  });
  $$('[data-product-rail]').forEach(rail => {
    const section = rail.closest('[data-rail-section]'); if (!section) return;
    const prev = $('[data-rail-prev]', section), next = $('[data-rail-next]', section), progress = $('.rail-progress span', section);
    rail.tabIndex = 0; rail.setAttribute('role','region'); rail.setAttribute('aria-label', (($('h2, h3', section) || {}).textContent || 'Prendas') + ': desliza para ver más');
    const update = () => {
      const max = Math.max(0, rail.scrollWidth - rail.clientWidth), position = Math.max(0, rail.scrollLeft);
      prev.disabled = position < 8; next.disabled = position >= max - 8; section.classList.toggle('rail-static', max < 8);
      const visible = rail.scrollWidth ? rail.clientWidth / rail.scrollWidth : 1;
      progress.style.width = `${visible * 100}%`; progress.style.transform = `translateX(${max ? position / max * (1 - visible) / visible * 100 : 0}%)`;
    };
    const step = () => { const card = rail.querySelector('.product-card'); const gap = parseFloat(getComputedStyle(rail).columnGap) || 0; const per = card ? card.getBoundingClientRect().width + gap : rail.clientWidth; return Math.max(per, Math.floor(rail.clientWidth / per) * per); };
    const move = direction => rail.scrollBy({left: direction * step(), behavior: reduced.matches ? 'instant' : 'smooth'});
    prev.addEventListener('click', () => move(-1)); next.addEventListener('click', () => move(1));
    rail.addEventListener('keydown', e => { if (e.target === rail && ['ArrowLeft','ArrowRight'].includes(e.key)) { e.preventDefault(); move(e.key === 'ArrowLeft' ? -1 : 1); } });
    rail.addEventListener('scroll', update, {passive:true}); new ResizeObserver(update).observe(rail); update();
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) $$('.category-jump a').forEach(a => a.classList.toggle('is-active', a.hash === '#' + entry.target.id));
    }), {rootMargin:'-10% 0px -65% 0px'}); $$('.category-group').forEach(section => observer.observe(section));
  }
  const genderListing = $('[data-gender-listing]');
  if (genderListing) {
    const groups = $$('[data-group-section]', genderListing), chips = $$('.filter-chips a'), sizeChips = $$('[data-size-filter]'), priceChips = $$('[data-price-filter]'), sort = $('[data-gender-sort]'), count = $('[data-gender-count]'), empty = $('[data-gender-empty]');
    const originals = new Map(groups.map(g => [g, [...$('[data-type-grid]', g).children]]));
    let active = 'all'; const sizes = new Set(); const prices = new Set();
    const apply = () => {
      let total = 0;
      groups.forEach(g => {
        const rail = $('[data-type-grid]', g);
        const cards = originals.get(g).filter(c => (!sizes.size || sizes.has(c.dataset.size)) && (!prices.size || prices.has(c.dataset.priceBand)));
        cards.sort((a,b) => sort.value === 'low' ? +a.dataset.price - +b.dataset.price : sort.value === 'high' ? +b.dataset.price - +a.dataset.price : 0);
        rail.replaceChildren(...cards); rail.scrollLeft = 0;
        const show = (active === 'all' || g.dataset.groupSection === active) && cards.length > 0; g.hidden = !show;
        const c = $('.type-count', g); if (c) c.textContent = `${cards.length} ${cards.length === 1 ? 'PIEZA' : 'PIEZAS'}`;
        if (show) total += cards.length; rail.dispatchEvent(new Event('scroll'));
      });
      count.textContent = `${total} ${total === 1 ? 'PIEZA ÚNICA' : 'PIEZAS ÚNICAS'}${sizes.size ? ' · TALLA ' + [...sizes].join(', ') : ''}`;
      empty.hidden = total > 0;
      chips.forEach(chip => { const on = chip.dataset.filter === active; chip.classList.toggle('is-active', on); chip.setAttribute('aria-pressed', String(on)); });
      sizeChips.forEach(chip => { const on = sizes.has(chip.dataset.sizeFilter); chip.classList.toggle('is-active', on); chip.setAttribute('aria-pressed', String(on)); });
      priceChips.forEach(chip => { const on = prices.has(chip.dataset.priceFilter); chip.classList.toggle('is-active', on); chip.setAttribute('aria-pressed', String(on)); });
    };
    const select = (filter, updateHash) => {
      if (!chips.some(c => c.dataset.filter === filter)) filter = 'all';
      active = filter; apply();
      if (updateHash) history.replaceState(null, '', filter === 'all' ? '#prendas' : '#' + filter);
    };
    const toBar = () => { const bar = $('.filter-bar'); if (bar.getBoundingClientRect().top > 120) bar.scrollIntoView({behavior: reduced.matches ? 'instant' : 'smooth'}); };
    chips.forEach(chip => chip.addEventListener('click', e => { e.preventDefault(); select(chip.dataset.filter, true); toBar(); }));
    sizeChips.forEach(chip => chip.addEventListener('click', () => { const z = chip.dataset.sizeFilter; sizes.has(z) ? sizes.delete(z) : sizes.add(z); apply(); }));
    priceChips.forEach(chip => chip.addEventListener('click', () => { const z = chip.dataset.priceFilter; prices.has(z) ? prices.delete(z) : prices.add(z); apply(); }));
    $('[data-clear-filters]')?.addEventListener('click', () => { sizes.clear(); prices.clear(); select('all', true); });
    sort.addEventListener('change', apply);
    const initial = location.hash.slice(1); if (initial && initial !== 'prendas') select(initial, false);
  }
  $$('[data-collection-grid]').forEach(grid => {
    const section = grid.closest('.collection-listing'), original = [...grid.children];
    const search = $('[data-collection-search]', section), sort = $('[data-collection-sort]', section), count = $('[data-collection-count]', section), empty = $('[data-collection-empty]', section);
    const sizeChips = $$('[data-size-filter]', section), priceChips = $$('[data-price-filter]', section);
    const sizes = new Set(), prices = new Set();
    count.setAttribute('aria-live','polite');
    const update = () => {
      const shown = original.filter(card => normalize(card.dataset.name).includes(normalize(search.value.trim())) && (!sizes.size || sizes.has(card.dataset.size)) && (!prices.size || prices.has(card.dataset.priceBand)));
      shown.sort((a,b) => sort.value === 'low' ? +a.dataset.price - +b.dataset.price : sort.value === 'high' ? +b.dataset.price - +a.dataset.price : original.indexOf(a) - original.indexOf(b));
      grid.replaceChildren(...shown); count.textContent = `${shown.length} ${shown.length === 1 ? 'pieza' : 'piezas'}`; empty.hidden = !!shown.length;
      sizeChips.forEach(chip => { const on = sizes.has(chip.dataset.sizeFilter); chip.classList.toggle('is-active', on); chip.setAttribute('aria-pressed', String(on)); });
      priceChips.forEach(chip => { const on = prices.has(chip.dataset.priceFilter); chip.classList.toggle('is-active', on); chip.setAttribute('aria-pressed', String(on)); });
    };
    const reset = document.createElement('button'); reset.type = 'button'; reset.textContent = 'Limpiar búsqueda';
    reset.addEventListener('click', () => { search.value = ''; sizes.clear(); prices.clear(); update(); search.focus(); }); empty.append(' ', reset);
    sizeChips.forEach(chip => chip.addEventListener('click', () => { const z = chip.dataset.sizeFilter; sizes.has(z) ? sizes.delete(z) : sizes.add(z); update(); }));
    priceChips.forEach(chip => chip.addEventListener('click', () => { const z = chip.dataset.priceFilter; prices.has(z) ? prices.delete(z) : prices.add(z); update(); }));
    search.addEventListener('input', update); sort.addEventListener('change', update);
  });
  // Comparador de medidas propias en la ficha de producto
  $$('[data-measure-row]').forEach(row => {
    const cm = parseFloat(row.dataset.cm), input = $('[data-measure-input]', row), diff = $('[data-measure-diff]', row);
    if (!input || !diff || isNaN(cm)) return;
    input.addEventListener('input', () => {
      const raw = input.value.replace(',', '.').trim();
      if (!raw) { diff.textContent = ''; delete diff.dataset.state; return; }
      const val = parseFloat(raw);
      if (isNaN(val)) { diff.textContent = ''; delete diff.dataset.state; return; }
      const delta = Math.round((val - cm) * 10) / 10, abs = Math.abs(delta);
      diff.dataset.state = abs <= 1 ? 'ok' : abs <= 3 ? 'warn' : 'bad';
      diff.textContent = abs < 0.1 ? 'Medida casi idéntica' : delta > 0 ? `+${delta.toFixed(1)} cm que la pieza` : `${delta.toFixed(1)} cm que la pieza`;
    });
  });
  // Micro-hover magnético en los botones principales
  if (matchMedia('(pointer: fine)').matches && !reduced.matches) {
    $$('.button.pink:not(.tag-cta)').forEach(btn => {
      btn.addEventListener('mousemove', e => {
        const r = btn.getBoundingClientRect();
        btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .16}px, ${(e.clientY - r.top - r.height / 2) * .32}px)`;
      });
      btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    });
  }
  // Scroll-reveal: se anima cuanto entra en la pantalla; lo ya visible aparece al instante (sin parpadeo)
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const targets = $$('.product-card, .section-heading, .category, .kids-category, .values > div, .story-grid > *, .brand-feature, .guide-block, .measure-panel');
    if (targets.length) {
      const io = new IntersectionObserver(entries => entries.forEach(entry => {
        if (entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }
      }), {threshold: .12, rootMargin: '0px 0px -60px 0px'});
      targets.forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.top < innerHeight * .94 && r.bottom > 0) el.classList.add('reveal', 'is-visible');
        else { el.classList.add('reveal'); io.observe(el); }
      });
    }
  }
  const form = $('[data-contact-form]');
  if (form) {
    const params = new URLSearchParams(location.search), status = $('[data-form-status]', form), submit = $('button[type="submit"]', form);
    const motivo = $('[data-field-motivo]', form), prenda = $('[data-field-prenda]', form);
    const key = params.get('motivo'); if (key) { const opt = [...motivo.options].find(o => o.dataset.key === key); if (opt) motivo.value = opt.value; }
    if (params.get('pieza')) prenda.value = params.get('pieza').slice(0, 300);
    $('[data-origin]', form).value = document.referrer || location.href;
    const say = (text, kind) => { status.hidden = false; status.className = 'form-status ' + (kind || ''); status.innerHTML = text; };
    if (params.get('enviado')) say('<strong>Mensaje enviado.</strong> Te responderemos por email lo antes posible.', 'ok');
    form.addEventListener('submit', async e => {
      e.preventDefault();
      $$('.field, .check', form).forEach(f => f.classList.remove('invalid'));
      const bad = [...form.elements].filter(el => el.willValidate && !el.checkValidity());
      if (bad.length) { bad.forEach(el => el.closest('.field, .check')?.classList.add('invalid')); say('Revisa los campos marcados: nombre, un email válido, un mensaje de al menos 10 caracteres y la casilla de privacidad.', 'error'); bad[0].focus(); return; }
      if (form.elements._honey.value) return;
      submit.disabled = true; submit.innerHTML = 'ENVIANDO… <span aria-hidden="true">↗</span>';
      try {
        const data = Object.fromEntries(new FormData(form));
        const res = await fetch(form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/'), {method:'POST', headers:{'Content-Type':'application/json', Accept:'application/json'}, body:JSON.stringify(data)});
        const json = await res.json().catch(() => ({}));
        if (!res.ok || String(json.success) === 'false') throw new Error(json.message || res.status);
        form.reset(); say('<strong>Mensaje enviado.</strong> Te responderemos por email lo antes posible.', 'ok');
      } catch (err) {
        say('No se ha podido enviar desde aquí. Escríbenos directamente a <a href="mailto:storedecada@gmail.com">storedecada@gmail.com</a>.', 'error');
      } finally { submit.disabled = false; submit.innerHTML = 'ENVIAR CONSULTA <span aria-hidden="true">↗</span>'; }
    });
  }
  const key = 'decada-preview-bag'; let bag = [];
  const validBag = value => Array.isArray(value) ? value.filter(p => p && typeof p.id === 'string' && /^[a-z0-9-]+$/.test(p.id) && typeof p.name === 'string' && typeof p.price === 'string') : [];
  try { bag = validBag(JSON.parse(localStorage.getItem(key) || '[]')); } catch {}
  const amount = item => Number(item.price.replace(/[^0-9,.-]/g,'').replace(',','.')) || 0;
  const assetPath = image => image.includes('/assets/') ? 'assets/' + image.split('/assets/').pop() : image.replace(/^(\.\.\/)+/, '');
  const buttons = $$('.add-preview'), proxies = $$('[data-proxy-add]');
  proxies.forEach(proxy => proxy.addEventListener('click', () => buttons[0]?.click()));
  const buyBar = $('[data-buy-bar]');
  if (buyBar && buttons[0] && 'IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      const show = !entry.isIntersecting;
      buyBar.classList.toggle('is-visible', show); buyBar.setAttribute('aria-hidden', String(!show));
      proxies.forEach(proxy => proxy.tabIndex = show ? 0 : -1);
    }).observe(buttons[0]);
  }
  const sync = () => {
    $$('[data-cart-count]').forEach(node => { node.textContent = bag.length; node.hidden = !bag.length; });
    $('.bag-link')?.setAttribute('aria-label', `Abrir bolsa: ${bag.length} ${bag.length === 1 ? 'prenda' : 'prendas'}`);
    buttons.forEach(button => {
      const added = bag.some(item => item.id === button.dataset.sku); button.disabled = added;
      button.innerHTML = added ? 'EN TU BOLSA <span aria-hidden="true">✓</span>' : 'AÑADIR A LA BOLSA <span aria-hidden="true">＋</span>';
      const link = $('.detail-bag-link', button.parentElement); if (link) link.hidden = !added;
    });
    const inBag = buttons[0] && bag.some(item => item.id === buttons[0].dataset.sku);
    proxies.forEach(proxy => { proxy.disabled = !!inBag; proxy.innerHTML = inBag ? 'EN TU BOLSA <span aria-hidden="true">✓</span>' : 'AÑADIR <span aria-hidden="true">＋</span>'; });
  };
  const save = () => { try { localStorage.setItem(key, JSON.stringify(bag)); } catch { notice('La bolsa no se puede guardar en este navegador.'); } sync(); };
  buttons.forEach(button => button.addEventListener('click', () => {
    if (bag.some(item => item.id === button.dataset.sku)) return;
    bag.push({id:button.dataset.sku, name:button.dataset.name, price:button.dataset.price, image:assetPath(button.dataset.image)}); save(); notice('Pieza añadida a tu bolsa.');
  }));
  const list = $('#bag-items'), empty = $('#bag-empty');
  const render = () => {
    if (!list) return;
    list.replaceChildren(); empty.hidden = !!bag.length; $('[data-bag-summary]').hidden = !bag.length; $('.bag-continue').hidden = !bag.length;
    $('[data-bag-quantity]').textContent = bag.length; $('[data-bag-total]').textContent = money(bag.reduce((sum,item) => sum + amount(item), 0));
    const enquiry = 'Hola DÉCADA, me gustaría consultar la disponibilidad de estas prendas:\n\n' + bag.map(item => `${item.name} — ${item.price}\nhttps://decada.store/productos/${item.id}/`).join('\n\n');
    $('.bag-summary .button').href = url('contacto/index.html') + '?motivo=pedido&pieza=' + encodeURIComponent(bag.map(item => `${item.name} (${item.price})`).join(' · ')) + '#formulario';
    bag.forEach(item => {
      const row = document.createElement('article'); row.className = 'bag-item';
      const imageLink = document.createElement('a'); imageLink.href = url(`productos/${item.id}/index.html`);
      const img = document.createElement('img'); img.src = url(assetPath(typeof item.image === 'string' ? item.image : 'assets/logo.webp')); img.alt = item.name; imageLink.append(img);
      const info = document.createElement('div'), title = document.createElement('h3'), price = document.createElement('p'), link = document.createElement('a');
      title.textContent = item.name; price.textContent = item.price; link.href = imageLink.href; link.textContent = 'VER LA PRENDA ↗'; info.append(title, price, link);
      const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = '×'; remove.setAttribute('aria-label', 'Quitar ' + item.name);
      remove.addEventListener('click', () => { bag = bag.filter(p => p.id !== item.id); save(); render(); notice('Pieza eliminada de la bolsa.'); (list.querySelector('button') || $('#bag-empty a')).focus(); });
      row.append(imageLink, info, remove); list.append(row);
    });
  };
  window.addEventListener('storage', e => { if (e.key === key) { try { bag = validBag(JSON.parse(e.newValue || '[]')); } catch {} sync(); render(); } });
  sync(); render();

  // Avisos superiores: rotan cada 4 s (quietos con «reducir movimiento»)
  const notes = $$('.announce p');
  if (notes.length > 1 && !reduced.matches) { let n = 0; setInterval(() => { if (document.hidden) return; notes[n].classList.remove('is-on'); n = (n + 1) % notes.length; notes[n].classList.add('is-on'); }, 4000); }

  // Buscador global
  const sDialog = $('[data-search-dialog]');
  if (sDialog) {
    const input = $('[data-search-input]', sDialog), results = $('[data-search-results]', sDialog), sCount = $('[data-search-count]', sDialog), brandsBox = $('[data-search-brands]', sDialog);
    let index = null;
    const load = () => index ? Promise.resolve(index) : Array.isArray(window.DECADA_SEARCH) ? Promise.resolve(index = window.DECADA_SEARCH) : fetch(url('assets/search-index.json')).then(r => r.json()).then(d => (index = d)).catch(() => (index = []));
    const esc = str => str.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    const mark = (text, words) => {
      if (!words.length) return esc(text);
      const n = normalize(text); const hits = new Array(text.length).fill(false);
      words.forEach(w => { if (!w) return; let i = n.indexOf(w); while (i > -1) { for (let k = i; k < i + w.length; k++) hits[k] = true; i = n.indexOf(w, i + 1); } });
      let out = '', open = false; [...text].forEach((ch, i) => { if (hits[i] && !open) { out += '<mark>'; open = true; } if (!hits[i] && open) { out += '</mark>'; open = false; } out += esc(ch); }); return out + (open ? '</mark>' : '');
    };
    const tile = (p, words, i) => {
      const li = document.createElement('li'); li.style.setProperty('--i', Math.min(i, 12));
      li.innerHTML = `<a href="${url(`productos/${p.slug}/index.html`)}"><span class="sr-photo"><img src="${url(p.img)}" alt="" loading="lazy" width="240" height="300">${p.img2 && p.img2 !== p.img ? `<img class="sr-back" src="${url(p.img2)}" alt="" loading="lazy" width="240" height="300">` : ''}<span class="sr-size">${esc(p.size)}</span></span><span class="sr-brand">${mark([p.brand, p.gender].filter(Boolean).join(' · ') || p.kind, words)}</span><strong>${mark(p.name, words)}</strong><span class="sr-foot"><span>${esc(p.kind)}</span><em>${esc(p.price)}</em></span></a>`;
      return li;
    };
    const latest = $('[data-search-latest]', sDialog);
    const draw = () => {
      const q = normalize(input.value.trim()); brandsBox.hidden = !!q; results.replaceChildren();
      if (latest && !latest.children.length && index) (index || []).slice(0, 6).forEach((p, i) => latest.append(tile(p, [], i)));
      if (!q) { sCount.textContent = ''; sCount.hidden = true; return; }
      sCount.hidden = false;
      const isSize = w => /^(xxs|xs|s|m|l|xl|xxl|\d{1,2})$/.test(w);
      const words = q.split(/\s+/).filter(w => w && w !== 'talla');
      const clean = s => normalize(s).replace(/['’]/g, '');
      const stem = w => w.length > 4 ? w.replace(/(es|s)$/, '') : w;
      const hits = (index || []).filter(p => { const hay = clean(`${p.name} ${p.brand} ${p.kind} ${p.gender}`); const size = normalize(p.sizeKey); return words.every(w => isSize(w) ? size === w || size.startsWith(w + ' ') : hay.includes(clean(w)) || hay.includes(stem(clean(w)))); }).slice(0, 36);
      sCount.innerHTML = hits.length ? `<strong>${hits.length}</strong> ${hits.length === 1 ? 'PIEZA ÚNICA' : 'PIEZAS ÚNICAS'} PARA «${esc(input.value.trim())}»` : `NADA PARA «${esc(input.value.trim())}». PRUEBA CON UNA MARCA O UNA TALLA:`;
      if (!hits.length) { const box = document.createElement('li'); box.className = 'sr-empty'; box.innerHTML = $('.search-suggest div', sDialog).innerHTML + [...$$('[data-search-brands] .search-suggest')[1].querySelectorAll('button')].slice(0, 5).map(b => b.outerHTML).join(''); results.append(box); return; }
      hits.forEach((p, i) => results.append(tile(p, words, i)));
    };
    let opener = null;
    const openSearch = term => { opener = document.activeElement; sDialog.showModal(); document.documentElement.classList.add('lb-open'); load().then(() => { input.value = term !== undefined ? term : input.value; draw(); }); setTimeout(() => input.focus(), 30); };
    $$('[data-search-open]').forEach(b => b.addEventListener('click', () => openSearch()));
    document.addEventListener('click', e => { const t = e.target.closest('[data-search-term]'); if (t) { if (!sDialog.open) openSearch(t.dataset.searchTerm); else { input.value = t.dataset.searchTerm; draw(); input.focus(); } } });
    input.addEventListener('input', draw);
    sDialog.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); sDialog.close(); } });
    $('[data-search-close]', sDialog).addEventListener('click', () => sDialog.close());
    sDialog.addEventListener('click', e => { if (e.target === sDialog) sDialog.close(); });
    sDialog.addEventListener('close', () => { document.documentElement.classList.remove('lb-open'); if (opener && opener.focus) opener.focus({preventScroll:true}); });
    document.addEventListener('keydown', e => { if ((e.key === '/' || (e.key.toLowerCase() === 'k' && (e.metaKey || e.ctrlKey))) && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !sDialog.open) { e.preventDefault(); openSearch(); } });
  }

  // Aviso de drops (email)
  $$('[data-drop-form]').forEach(f => {
    const st = $('[data-drop-status]', f), btn = $('button[type="submit"]', f);
    f.addEventListener('submit', async e => {
      e.preventDefault();
      const bad = [...f.elements].filter(el => el.willValidate && !el.checkValidity());
      if (bad.length) { st.hidden = false; st.className = 'drop-form-status error'; st.textContent = bad[0].type === 'checkbox' ? 'Marca la casilla de privacidad para apuntarte.' : 'Escribe un email válido.'; bad[0].focus(); return; }
      if (f.elements._honey?.value) return;
      btn.disabled = true;
      try {
        const res = await fetch(f.action.replace('formsubmit.co/', 'formsubmit.co/ajax/'), {method:'POST', headers:{'Content-Type':'application/json', Accept:'application/json'}, body:JSON.stringify(Object.fromEntries(new FormData(f)))});
        const json = await res.json().catch(() => ({})); if (!res.ok || String(json.success) === 'false') throw new Error();
        f.reset(); st.hidden = false; st.className = 'drop-form-status ok'; st.textContent = 'Hecho. Te avisaremos del próximo drop.';
      } catch { st.hidden = false; st.className = 'drop-form-status error'; st.innerHTML = 'No se ha podido enviar. Escríbenos a <a href="mailto:storedecada@gmail.com">storedecada@gmail.com</a>.'; }
      finally { btn.disabled = false; }
    });
  });

  // Desplegable con el estilo de DÉCADA sobre el <select> nativo (que sigue funcionando sin JavaScript).
  let ddCount = 0;
  $$('select[data-gender-sort], select[data-collection-sort]').forEach(select => {
    const id = 'dd-' + (++ddCount), wrap = document.createElement('div'); wrap.className = 'dd';
    const button = document.createElement('button'); button.type = 'button'; button.className = 'dd-button'; button.setAttribute('aria-haspopup','listbox'); button.setAttribute('aria-expanded','false'); button.setAttribute('aria-controls', id);
    button.setAttribute('aria-label', 'Ordenar: ' + select.selectedOptions[0].textContent);
    const list = document.createElement('ul'); list.className = 'dd-list'; list.id = id; list.setAttribute('role','listbox'); list.hidden = true; list.tabIndex = -1;
    const items = [...select.options].map((opt, i) => { const li = document.createElement('li'); li.setAttribute('role','option'); li.id = `${id}-${i}`; li.dataset.value = opt.value; li.innerHTML = `<span>${opt.textContent}</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>`; list.append(li); return li; });
    let active = select.selectedIndex;
    const paint = () => { const opt = select.selectedOptions[0]; button.innerHTML = `<span>${opt.dataset.short || opt.textContent}</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>`; button.setAttribute('aria-label', 'Ordenar: ' + opt.textContent); items.forEach((li, i) => { li.setAttribute('aria-selected', String(i === select.selectedIndex)); li.classList.toggle('is-active', i === active); }); list.setAttribute('aria-activedescendant', items[active].id); };
    const open = () => { active = select.selectedIndex; list.hidden = false; wrap.classList.add('open'); button.setAttribute('aria-expanded','true'); paint(); list.focus(); };
    const close = focus => { list.hidden = true; wrap.classList.remove('open'); button.setAttribute('aria-expanded','false'); if (focus) button.focus(); };
    const choose = i => { select.selectedIndex = i; select.dispatchEvent(new Event('change', {bubbles:true})); active = i; paint(); close(true); };
    button.addEventListener('click', () => list.hidden ? open() : close(false));
    button.addEventListener('keydown', e => { if (['ArrowDown','ArrowUp'].includes(e.key)) { e.preventDefault(); open(); } });
    items.forEach((li, i) => { li.addEventListener('click', () => choose(i)); li.addEventListener('mousemove', () => { if (active !== i) { active = i; paint(); } }); });
    list.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { e.preventDefault(); active = Math.min(items.length - 1, active + 1); paint(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); active = Math.max(0, active - 1); paint(); }
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(active); }
      else if (e.key === 'Escape' || e.key === 'Tab') close(e.key === 'Escape');
    });
    document.addEventListener('click', e => { if (!e.composedPath().includes(wrap)) close(false); });
    select.classList.add('dd-native'); select.tabIndex = -1; select.setAttribute('aria-hidden','true');
    wrap.addEventListener('click', e => e.preventDefault()); // evita que la etiqueta <label> reenvíe el clic al select oculto
    select.after(wrap); wrap.append(button, list); paint();
  });

  // Asistente de DÉCADA: chat simulado con respuestas reales del sitio (sin backend) + salida a WhatsApp
  const chatWidget = $('[data-chat-widget]');
  if (chatWidget) {
    const panel = $('[data-chat-panel]', chatWidget), fab = $('[data-chat-toggle]', chatWidget), closeBtn = $('[data-chat-close]', chatWidget);
    const body = $('[data-chat-body]', chatWidget), chipsBox = $('[data-chat-chips]', chatWidget), form = $('[data-chat-form]', chatWidget), input = $('[data-chat-input]', chatWidget);
    const topics = [
      {
        id: 'tallas', label: '¿Cómo van las tallas?', keywords: ['talla','tallas','medida','medidas','ajuste','tallaje','size'],
        answer: `El tallaje vintage rara vez coincide con el actual. Cada ficha incluye las medidas reales (pecho, hombros, cintura, largo) tomadas a mano, y puedes compararlas al momento con una prenda tuya en el comparador de la propia ficha. Tienes también una <a href="${url('guia-tallas/index.html')}">guía de tallas completa ↗</a>.`
      },
      {
        id: 'estado', label: '¿Qué significa el estado de una prenda?', keywords: ['estado','condicion','condición','uso','defecto','defectos'],
        answer: '<strong>Excelente estado</strong>: sin marcas de uso visibles. <strong>Muy buen estado</strong>: uso ligero, sin defectos que afecten a la prenda. <strong>Buen estado</strong>: señales de uso o pequeños detalles, siempre indicados y fotografiados en la ficha.'
      },
      {
        id: 'autenticidad', label: '¿Cómo sé que es original?', keywords: ['original','autentico','auténtico','autenticidad','falso','falsificacion','falsificación','replica','réplica'],
        answer: 'Revisamos etiquetas, costuras y detalles de cada pieza antes de publicarla. Si una prenda genera dudas sobre su autenticidad, no entra en DÉCADA. Si quieres ver una etiqueta o un detalle concreto de una prenda, pídenoslo aquí o por WhatsApp.'
      },
      {
        id: 'comprar', label: '¿Cómo funciona la compra y el envío?', keywords: ['comprar','compra','pedido','envio','envío','devolucion','devolución','pago','reserva','reservar'],
        answer: `Explora el catálogo, abre la ficha para ver fotos, talla y medidas, y añade la pieza a tu bolsa. Ojo: añadir a la bolsa no reserva la pieza, se la lleva quien complete antes la compra. Para dudas sobre pedido, envío o devoluciones, escríbenos. Tienes el detalle completo en <a href="${url('como-comprar/index.html')}">cómo comprar ↗</a>.`
      },
      {
        id: 'vinted', label: '¿Vendéis también en Vinted?', keywords: ['vinted'],
        answer: `Sí, parte del archivo también está en nuestro perfil de Vinted. Si tienes dudas sobre una pieza en concreto, dínoslo y te ayudamos. Más info en <a href="${url('contacto/index.html')}#vinted">contacto ↗</a>.`
      }
    ];
    const humanLink = $('.chat-human', chatWidget);
    const scrollDown = () => { body.scrollTop = body.scrollHeight; };
    const addBubble = (text, from) => {
      const p = document.createElement('p'); p.className = 'chat-bubble chat-' + from; p.innerHTML = text; body.append(p); scrollDown(); return p;
    };
    const renderChips = (excludeId) => {
      chipsBox.replaceChildren();
      topics.filter(t => t.id !== excludeId).forEach(t => {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'chat-chip'; b.textContent = t.label;
        b.addEventListener('click', () => ask(t)); chipsBox.append(b);
      });
      const human = document.createElement('button'); human.type = 'button'; human.className = 'chat-chip chat-chip-human'; human.textContent = 'Hablar con una persona ↗';
      human.addEventListener('click', () => humanLink.click()); chipsBox.append(human);
    };
    const typing = () => {
      const p = addBubble('<span></span><span></span><span></span>', 'bot typing'); return p;
    };
    const ask = topic => {
      addBubble(topic.label, 'user');
      const t = typing();
      setTimeout(() => { t.remove(); addBubble(topic.answer, 'bot'); renderChips(topic.id); }, reduced.matches ? 0 : 420);
    };
    const matchTopic = raw => {
      const q = normalize(raw);
      return topics.find(t => t.keywords.some(k => q.includes(normalize(k))));
    };
    let greeted = false;
    const greet = () => {
      if (greeted) return; greeted = true;
      addBubble('Hola 👋 Soy el asistente de DÉCADA. Puedo ayudarte con esto:', 'bot');
      renderChips();
    };
    const setOpen = open => {
      chatWidget.classList.toggle('is-open', open);
      fab.setAttribute('aria-expanded', String(open));
      fab.setAttribute('aria-label', open ? 'Cerrar chat de ayuda' : 'Abrir chat de ayuda de DÉCADA');
      if (open) { greet(); setTimeout(() => input.focus(), 200); }
    };
    fab.addEventListener('click', () => setOpen(!chatWidget.classList.contains('is-open')));
    closeBtn.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && chatWidget.classList.contains('is-open')) { setOpen(false); fab.focus(); } });
    form.addEventListener('submit', e => {
      e.preventDefault();
      const value = input.value.trim(); if (!value) return;
      input.value = '';
      addBubble(value.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])), 'user');
      const match = matchTopic(value);
      const t = typing();
      setTimeout(() => {
        t.remove();
        if (match) { addBubble(match.answer, 'bot'); renderChips(match.id); }
        else { addBubble('No tengo una respuesta preparada para eso todavía. Cuéntanoslo por WhatsApp y te contestamos en persona.', 'bot'); renderChips(); }
      }, reduced.matches ? 0 : 420);
    });
  }
})();
