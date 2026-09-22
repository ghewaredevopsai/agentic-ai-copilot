/* ===========================================================================
   Python Accelerated - slide runner
   Plain ES5-ish DOM, no dependencies, no CDN. Works from file:// and offline.

   A deck only authors <section class="slide">...</section> blocks.
   Branding, footers, counter, index and notes are injected from here, so the
   whole module is re-branded by editing this file and py-theme.css.

   Keys:  arrows / space / PgUp / PgDn / Home / End  navigate
          T index      N notes      F fullscreen      Esc close
   =========================================================================== */
(function () {
  'use strict';

  var BRAND = {
    org:   'Gheware DevOps &amp; Agentic AI',
    site:  'devops.gheware.com',
    siteU: 'https://devops.gheware.com',
    mail:  'training@gheware.com',
    phone: '+91-9606795215',
    trainer: 'Rajesh Gheware'
  };

  var stage  = document.getElementById('stage');
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  var d      = document.body.dataset;
  var deck   = d.deck || 'Python Accelerated';
  var home   = d.home || '../index.html';
  var cur    = 0;

  /* ---- chrome -------------------------------------------------------- */
  function el(html) { var t = document.createElement('div'); t.innerHTML = html; return t.firstChild; }

  document.body.appendChild(el('<div id="bar"><i></i></div>'));
  document.body.appendChild(el(
    '<div id="hud">' +
      '<a href="' + home + '" title="Module home">MODULE</a><span class="sep">|</span>' +
      (d.prev ? '<a href="' + d.prev + '" title="' + (d.prevLabel || '') + '">&#8592; prev</a><span class="sep">|</span>' : '') +
      (d.next ? '<a href="' + d.next + '" title="' + (d.nextLabel || '') + '">next &#8594;</a><span class="sep">|</span>' : '') +
      '<a href="#" data-act="index">index</a><span class="sep">|</span>' +
      '<a href="#" data-act="notes">notes</a><span class="sep">|</span>' +
      '<span id="count">1 / ' + slides.length + '</span>' +
    '</div>'));
  document.body.appendChild(el(
    '<div class="overlay" id="indexOv"><h3>' + deck + '</h3>' +
    '<p class="hint">click a slide, or press T to close</p><div id="indexList"></div></div>'));
  document.body.appendChild(el(
    '<div class="overlay" id="notesOv"><h3>Notes</h3>' +
    '<p class="hint">press N to close</p><div id="notesBody"></div></div>'));

  var bar = document.querySelector('#bar > i');
  var count = document.getElementById('count');
  var indexOv = document.getElementById('indexOv');
  var notesOv = document.getElementById('notesOv');
  var notesBody = document.getElementById('notesBody');

  /* ---- syntax highlighting for every <pre> ---------------------------- */
  /* Language-agnostic and deliberately small: strings, comments, decorators,
     numbers, keywords. Text already inside a deck's own <i>/<u>/<s>/<em>
     marks is left alone, so hand-made emphasis always wins. */
  var KW = ('def class return if elif else for in while import from as with try except finally raise ' +
    'async await lambda yield not and or is None True False pass break continue del assert self ' +
    'public private static var const let function new this null true false type interface record ' +
    'string int bool void using extends implements endfor endif block include').split(' ');
  var KWSET = {}; KW.forEach(function (w) { KWSET[w] = 1; });
  var TOKEN = /("""|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|((?:#|\/\/)[^\n]*)|(@[A-Za-z_][\w.]*)|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_]\w*\b)/g;
  function highlight(node) {
    var text = node.nodeValue, frag = document.createDocumentFragment(), last = 0, m, cls;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(text))) {
      if (m[1]) cls = 's'; else if (m[2]) cls = 'c'; else if (m[3]) cls = 'd';
      else if (m[4]) cls = 'n'; else cls = KWSET[m[5]] ? 'k' : null;
      if (!cls) continue;
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      var sp = document.createElement('span'); sp.className = cls; sp.textContent = m[0];
      frag.appendChild(sp); last = m.index + m[0].length;
    }
    if (!last) return;
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }
  [].forEach.call(document.querySelectorAll('.slide pre'), function (pre) {
    var walker = document.createTreeWalker(pre, NodeFilter.SHOW_TEXT, null, false), nodes = [], n;
    while ((n = walker.nextNode())) {
      var p = n.parentNode, skip = false;
      while (p && p !== pre) { if (/^(I|U|S|EM)$/.test(p.tagName)) { skip = true; break; } p = p.parentNode; }
      if (!skip) nodes.push(n);
    }
    nodes.forEach(highlight);
  });

  /* ---- footer on every slide ----------------------------------------- */
  slides.forEach(function (s, i) {
    if (s.querySelector(':scope > footer')) return;
    var f = document.createElement('footer');
    f.innerHTML =
      '<span class="brand"><b>' + BRAND.org + '</b> &middot; ' +
        '<a href="' + BRAND.siteU + '">' + BRAND.site + '</a> &middot; ' +
        BRAND.mail + ' &middot; ' + BRAND.phone + '</span>' +
      '<span>' + deck + ' &middot; Trainer: ' + BRAND.trainer + '</span>';
    s.appendChild(f);
  });

  /* ---- fit each slide's content to its space --------------------------- */
  /* Decks are read from across a room, so every slide's .body is zoomed to the
     largest size at which nothing overflows and no code line is clipped:
     sparse slides grow, dense ones shrink a little. Computed once per slide,
     the first time it is shown (a hidden slide cannot be measured). */
  var FIT_MIN = 0.8, FIT_MAX = 1.45;
  function overflowing(sl) {
    if (sl.scrollHeight > sl.clientHeight + 1 || sl.scrollWidth > sl.clientWidth + 1) return true;
    var box = sl.getBoundingClientRect(), foot = sl.querySelector(':scope > footer');
    if (foot && foot.getBoundingClientRect().bottom > box.bottom + 1) return true;
    var head = sl.querySelector(':scope > header');                 // unzoomed: marks the content edge
    var edge = head ? head.getBoundingClientRect().right : box.right;
    var top = head ? head.getBoundingClientRect().bottom : box.top;
    var bottom = foot ? foot.getBoundingClientRect().top : box.bottom;
    var parts = sl.querySelectorAll(':scope > .body > *, :scope > .body .card, :scope > .body table, :scope > .body pre, :scope > .body svg');
    for (var j = 0; j < parts.length; j++) {
      var r = parts[j].getBoundingClientRect();
      if (r.right > edge + 1 || r.top < top - 1 || r.bottom > bottom + 1) return true;
    }
    var boxes = sl.querySelectorAll(':scope > .body');   /* would it need to scroll? */
    for (var q = 0; q < boxes.length; q++) {
      if (boxes[q].scrollHeight > boxes[q].clientHeight + 1 || boxes[q].scrollWidth > boxes[q].clientWidth + 1) return true;
    }
    var pres = sl.querySelectorAll('pre');
    for (var i = 0; i < pres.length; i++) {
      if (pres[i].scrollWidth > pres[i].clientWidth + 1) return true;
      if (pres[i].getBoundingClientRect().right > edge + 1) return true;
    }
    return false;
  }
  function fitSlide(sl) {
    var body = sl.querySelector(':scope > .body');
    if (!body || sl.getAttribute('data-fitted')) return;
    var lo = FIT_MIN, hi = FIT_MAX;
    body.style.zoom = hi;
    if (overflowing(sl)) {
      for (var k = 0; k < 9; k++) {
        var mid = (lo + hi) / 2;
        body.style.zoom = mid;
        if (overflowing(sl)) hi = mid; else lo = mid;
      }
      body.style.zoom = lo;
    }
    /* leave slack, then confirm: a scrollbar shown mid-search can skew the last measurement */
    var z = parseFloat(body.style.zoom) * 0.97;
    body.style.zoom = z;
    while (overflowing(sl) && z > FIT_MIN) { z = Math.max(FIT_MIN, z - 0.03); body.style.zoom = z; }
    sl.setAttribute('data-fitted', body.style.zoom);
  }
  window.__fitSlide = fitSlide;

  /* ---- index --------------------------------------------------------- */
  function titleOf(h) {
    var c = h.cloneNode(true);                 // a <br> in a title is a line break,
    [].forEach.call(c.querySelectorAll('br'),  // not a word join
      function (b) { b.parentNode.replaceChild(document.createTextNode(' '), b); });
    return c.textContent.replace(/\s+/g, ' ').trim();
  }

  var list = document.getElementById('indexList');
  slides.forEach(function (s, i) {
    var h = s.querySelector('h1, h2');
    var a = el('<a href="#/' + (i + 1) + '"><span class="n">' +
      (i + 1 < 10 ? '0' : '') + (i + 1) + '</span>' +
      (h ? titleOf(h) : 'Slide ' + (i + 1)) + '</a>');
    a.addEventListener('click', function () { closeOverlays(); });
    list.appendChild(a);
  });
  var links = [].slice.call(list.children);

  /* ---- scaling ------------------------------------------------------- */
  function fit() {
    var s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    stage.style.transform = 'scale(' + s + ')';
  }

  /* ---- navigation ---------------------------------------------------- */
  function show(n) {
    cur = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (s, i) { s.classList.toggle('active', i === cur); });
    fitSlide(slides[cur]);
    links.forEach(function (a, i) { a.classList.toggle('cur', i === cur); });
    bar.style.width = ((cur + 1) / slides.length * 100) + '%';
    count.textContent = (cur + 1) + ' / ' + slides.length;
    var nt = slides[cur].querySelector('.notes');
    notesBody.innerHTML = nt ? nt.innerHTML : '<p style="color:var(--fg-faint)">No notes for this slide.</p>';
    if (history.replaceState) history.replaceState(null, '', '#/' + (cur + 1));
  }
  function closeOverlays() { indexOv.classList.remove('open'); notesOv.classList.remove('open'); }
  function toggle(ov) { var was = ov.classList.contains('open'); closeOverlays(); if (!was) ov.classList.add('open'); }

  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var k = e.key;
    if (k === 'ArrowRight' || k === 'PageDown' || k === ' ') { show(cur + 1); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { show(cur - 1); e.preventDefault(); }
    else if (k === 'Home') { show(0); }
    else if (k === 'End') { show(slides.length - 1); }
    else if (k === 't' || k === 'T') { toggle(indexOv); }
    else if (k === 'n' || k === 'N') { toggle(notesOv); }
    else if (k === 'f' || k === 'F') {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    }
    else if (k === 'Escape') { closeOverlays(); }
  });

  document.getElementById('hud').addEventListener('click', function (e) {
    var act = e.target.getAttribute('data-act');
    if (!act) return;
    e.preventDefault();
    toggle(act === 'index' ? indexOv : notesOv);
  });

  [indexOv, notesOv].forEach(function (ov) {
    ov.addEventListener('click', function (e) { if (e.target === ov) closeOverlays(); });
  });

  /* click / swipe on the stage */
  var x0 = null;
  stage.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  stage.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 45) show(cur + (dx < 0 ? 1 : -1));
    x0 = null;
  }, { passive: true });

  window.addEventListener('resize', fit);
  window.addEventListener('hashchange', function () {
    var m = /^#\/(\d+)/.exec(location.hash);
    if (m) show(parseInt(m[1], 10) - 1);
  });

  fit();
  var m = /^#\/(\d+)/.exec(location.hash);
  show(m ? parseInt(m[1], 10) - 1 : 0);

  /* a fit measured before the final font is in use is wrong: measure again */
  function refit() {
    slides.forEach(function (s) { s.removeAttribute('data-fitted'); });
    fitSlide(slides[cur]);
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  window.addEventListener('load', refit);
  var resizeTimer;
  window.addEventListener('resize', function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(refit, 150); });
})();
