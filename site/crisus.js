// crisus.js: everything the site does in the browser.

// Clocks: every element with data-since="ISO time" counts up from that moment, and
// every element with data-until counts down to it, in days and hh:mm:ss. Without
// JavaScript the element keeps the text it has in the page.
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
    var since = b.hasAttribute('data-since'), t = Date.parse(b.getAttribute(since ? 'data-since' : 'data-until'));
    if (isNaN(t)) return;
    function tick() {
      var s = Math.max(0, Math.round((since ? Date.now() - t : t - Date.now()) / 1000));
      var d = Math.floor(s / 86400), hms = [Math.floor(s / 3600) % 24, Math.floor(s / 60) % 60, s % 60]
        .map(function (n) { return String(n).padStart(2, '0'); }).join(':');
      b.textContent = (d ? days(d) : '') + hms;
      setTimeout(tick, 1000);
    }
    tick();
  }
  var els = document.querySelectorAll('[data-since], [data-until]');
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

// The hourly round: controle.js (written by tools/controle.py, not in git) says when
// the last round looked and whether it found news. Without it the line stays hidden.
(function () {
  var el = document.getElementById('controle'), c = window.crisusControle;
  var m = c && /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})/.exec(c.at);
  if (!el || !m) return;
  var MAANDEN = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
                 'augustus', 'september', 'oktober', 'november', 'december'];
  var vandaag = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Amsterdam' }).format(new Date());
  var d = m[1].split('-'), time = el.querySelector('time');
  time.setAttribute('datetime', c.at);
  time.textContent = (m[1] === vandaag ? '' : Number(d[2]) + ' ' + MAANDEN[d[1] - 1] + ', ') + m[2];
  // A round with news bumps the page after it looked: then the stamp says so too
  var bijgewerkt = Date.parse(document.querySelector('.kicker time').getAttribute('datetime'));
  el.querySelector('.uitslag').textContent = c.nieuws || bijgewerkt >= Date.parse(c.at) ? 'nieuwe update' : 'niets nieuws';
  el.hidden = false;
})();

// On the anniversary of an earlier crisus (a full date in the archive list), say so
// at the top of the page.
(function () {
  var el = document.getElementById('vandaag');
  if (!el) return;
  var nu = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Amsterdam' }).format(new Date());
  var items = document.querySelectorAll('.archief li');
  for (var i = 0; i < items.length; i++) {
    var dt = items[i].querySelector('time').getAttribute('datetime'), jaren = nu.slice(0, 4) - dt.slice(0, 4);
    if (dt.length !== 10 || dt.slice(5) !== nu.slice(5) || jaren < 1) continue;
    var a = document.createElement('a');
    a.href = '#archief';
    a.textContent = items[i].querySelector('b').textContent;
    el.textContent = 'Vandaag ' + jaren + ' jaar geleden: ';
    el.appendChild(a);
    el.appendChild(document.createTextNode('.'));
    el.hidden = false;
    return;
  }
})();

// The next Patch Tuesday: the second Tuesday of the month, today included.
(function () {
  var el = document.getElementById('patchdinsdag');
  if (!el) return;
  var MAANDEN = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
                 'augustus', 'september', 'oktober', 'november', 'december'];
  var n = new Date(), vandaag = new Date(n.getFullYear(), n.getMonth(), n.getDate());
  function tweede(j, m) { var d = new Date(j, m, 1); d.setDate(1 + (9 - d.getDay()) % 7 + 7); return d; }
  var pd = tweede(vandaag.getFullYear(), vandaag.getMonth());
  if (pd < vandaag) pd = tweede(vandaag.getFullYear(), vandaag.getMonth() + 1);
  var dagen = Math.round((pd - vandaag) / 86400000);
  el.textContent = pd.getDate() + ' ' + MAANDEN[pd.getMonth()] +
    (dagen === 0 ? ', vandaag' : dagen === 1 ? ', morgen' : ', over ' + dagen + ' dagen');
})();

// Red for a while: an element with data-rood="START/END" (ISO) gets the class "rood"
// in that window, and shows its .nu text. Winter time: from 02:00 summer time until
// it is really 03:00, the second time round.
(function () {
  var els = document.querySelectorAll('[data-rood]');
  if (!els.length) return;
  function kijk() {
    var nu = Date.now();
    for (var i = 0; i < els.length; i++) {
      var p = els[i].getAttribute('data-rood').split('/');
      var aan = nu >= Date.parse(p[0]) && nu < Date.parse(p[1]);
      els[i].classList.toggle('rood', aan);
      var t = els[i].querySelector('.nu');
      if (t) t.hidden = !aan;
    }
  }
  kijk();
  setInterval(kijk, 30000);
})();
