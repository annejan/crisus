// Clocks: every <b data-since="ISO time"> counts up from that moment, in days and
// hh:mm:ss. Without JavaScript the element keeps the text it has in the page.
(function () {
  var lang = (document.documentElement.lang || 'nl').slice(0, 2);
  function days(d) {
    if (lang === 'en') return d + (d === 1 ? ' day ' : ' days ');
    if (lang === 'uk') {
      var t = d % 10, h = d % 100;
      return d + (t === 1 && h !== 11 ? ' день ' : t >= 2 && t <= 4 && (h < 12 || h > 14) ? ' дні ' : ' днів ');
    }
    return d + (d === 1 ? ' dag ' : ' dagen ');
  }
  function start(b) {
    var t = Date.parse(b.getAttribute('data-since'));
    if (isNaN(t)) return;
    function tick() {
      var s = Math.max(0, Math.round((Date.now() - t) / 1000));
      var d = Math.floor(s / 86400), hms = [Math.floor(s / 3600) % 24, Math.floor(s / 60) % 60, s % 60]
        .map(function (n) { return String(n).padStart(2, '0'); }).join(':');
      b.textContent = (d ? days(d) : '') + hms;
      setTimeout(tick, 1000);
    }
    tick();
  }
  var els = document.querySelectorAll('b[data-since]');
  for (var i = 0; i < els.length; i++) start(els[i]);
})();

// The zo-meter: how long "We zijn zo terug" has lasted on overheid.nl, counted
// from 20:27 on 21 October, when NOS reported the site still offline. The
// element only exists while the site is down; without JavaScript it says "een tijdje".
(function () {
  var b = document.getElementById('zo'), t = Date.UTC(2026, 9, 21, 18, 27, 0);
  if (!b) return;
  function tick() {
    var s = Math.max(0, Math.round((Date.now() - t) / 1000));
    b.textContent = Math.floor(s / 3600) + ' uur, ' + (Math.floor(s / 60) % 60) + ' minuten en ' + (s % 60) + ' seconden';
    setTimeout(tick, 1000);
  }
  tick();
})();

// An update that is no longer on the front page lives in the archive of its
// crisis: send an old https://crisus.nl/#u-YYYYMMDD-HHMM link on to it.
(function () {
  var ARCHIVES = [{ from: '20261020', to: '20261023', path: '/php/' }];
  var m = /^#u-(\d{8})-\d{4}$/.exec(location.hash);
  if (location.pathname !== '/' || !m || document.getElementById(location.hash.slice(1))) return;
  for (var i = 0; i < ARCHIVES.length; i++) {
    if (m[1] >= ARCHIVES[i].from && m[1] <= ARCHIVES[i].to) { location.replace(ARCHIVES[i].path + location.hash); return; }
  }
})();

// A link to an older update, or to a folded step, opens its <details> first and
// then scrolls there: the browser cannot scroll to something that is folded away.
(function () {
  function unfold() {
    var id = decodeURIComponent(location.hash.slice(1)), el = id && document.getElementById(id), folded = false;
    for (var p = el; p; p = p.parentElement) if (p.tagName === 'DETAILS' && !p.open) { p.open = true; folded = true; }
    if (folded) el.scrollIntoView();
  }
  unfold();
  window.addEventListener('hashchange', unfold);
})();

// The hum of business as usual: 50 Hz, like the grid, with the 100 and 150 Hz
// overtones small speakers can actually play. Only on a click, never by itself.
(function () {
  var btn = document.getElementById('brom');
  if (!btn || !(window.AudioContext || window.webkitAudioContext)) return;
  btn.hidden = false;
  var ctx = null, out = null, oscs = [];
  btn.addEventListener('click', function () {
    if (out) {
      out.gain.setTargetAtTime(0, ctx.currentTime, 0.15);
      var o = out, running = oscs; out = null; oscs = [];
      setTimeout(function () { running.forEach(function (x) { x.stop(); }); o.disconnect(); }, 800);
      btn.setAttribute('aria-pressed', 'false');
      btn.textContent = btn.getAttribute('data-off');
      return;
    }
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    out = ctx.createGain();
    out.gain.value = 0;
    out.connect(ctx.destination);
    [[50, 0.5], [100, 0.3], [150, 0.15], [250, 0.05]].forEach(function (h) {
      var osc = ctx.createOscillator(), g = ctx.createGain();
      osc.frequency.value = h[0];
      g.gain.value = h[1];
      osc.connect(g); g.connect(out); osc.start(); oscs.push(osc);
    });
    out.gain.setTargetAtTime(0.08, ctx.currentTime, 0.3);
    btn.setAttribute('aria-pressed', 'true');
    btn.textContent = btn.getAttribute('data-on');
  });
})();
