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

// The nights the clocks change, both on the last Sunday of the month at 01:00 UTC.
// October, back: from the first 02:00 until the real, second 03:00 (00:00-02:00 UTC).
// March, forward: 02:00 becomes 03:00, so the first hour of summer time (01:00-02:00 UTC)
// is spent looking for the lost one. Then the level goes to red, 5 of 5. Only on the
// live pages, not in the archive. ?wintertijd and ?zomertijd show it any time.
(function () {
  var h = document.getElementById('niveau'), lis = document.querySelectorAll('.level ol li');
  if (!h || lis.length !== 6 || /^\/(php|museum)\//.test(location.pathname)) return;
  function zondag(j, m) { var d = new Date(Date.UTC(j, m + 1, 0)); d.setUTCDate(d.getUTCDate() - d.getUTCDay()); return d.getTime(); }
  var nu = Date.now(), j = new Date(nu).getUTCFullYear(), u = 3600000;
  var winter = zondag(j, 9), zomer = zondag(j, 2) + u;
  var welke = /[?&]wintertijd\b/.test(location.search) || (nu >= winter && nu < winter + 2 * u) ? 'winter'
            : /[?&]zomertijd\b/.test(location.search) || (nu >= zomer && nu < zomer + u) ? 'zomer' : null;
  if (!welke) return;
  var T = {
    winter: {
      nl: ['Huidig crisusniveau: 5 van 5. Wintertijd.',
           'Om 3 uur is het weer 2 uur. Het crisusteam beleeft dit uur twee keer en snapt het nog steeds niet. Bij het echte 3 uur, het tweede, zakt het niveau vanzelf terug.'],
      en: ['Current crisis level: 5 of 5. The clocks go back.',
           'At 3 o’clock it is 2 o’clock again. The crisis team lives through this hour twice and still does not get it. At the real 3 o’clock, the second one, the level drops back by itself.'],
      uk: ['Поточний рівень кризи: 5 з 5. Перехід на зимовий час.',
           'О третій знову друга. Кризова команда проживає цю годину двічі й досі нічого не розуміє. О справжній третій, другій за ліком, рівень повернеться сам.']
    },
    zomer: {
      nl: ['Huidig crisusniveau: 5 van 5. Zomertijd.',
           'Om 2 uur was het ineens 3 uur. Het uur daartussen is weg. Het crisusteam zoekt het nog. Om 4 uur geeft het de zoektocht op en zakt het niveau vanzelf terug.'],
      en: ['Current crisis level: 5 of 5. The clocks go forward.',
           'At 2 o’clock it was suddenly 3 o’clock. The hour in between is gone. The crisis team is still looking for it. At 4 o’clock it gives up and the level drops back by itself.'],
      uk: ['Поточний рівень кризи: 5 з 5. Перехід на літній час.',
           'О другій раптом стала третя. Година між ними зникла. Кризова команда досі її шукає. О четвертій пошуки припиняться, і рівень повернеться сам.']
    }
  }[welke][(document.documentElement.lang || 'nl').slice(0, 2)] || null;
  if (!T) return;
  for (var i = 0; i < 6; i++) {
    lis[i].className = i < 5 ? 'on' : 'now';
    if (i < 5) lis[i].removeAttribute('aria-current'); else lis[i].setAttribute('aria-current', 'step');
  }
  h.textContent = T[0];
  var p = document.createElement('p');
  p.className = 'wintertijd';
  p.textContent = T[1];
  h.parentNode.classList.add('rood');
  h.parentNode.appendChild(p);
})();

// Easter egg (29 October 2026, the Binance drain): type "boe" or "binance", or click
// the headline or the logo three times, and a ghost floats across the page taking the bitcoins.
// Type "wiccon", or keep the WICCON radar item in view (WICCON 2026, 29 and 30 October),
// and a team chases it off instead.
// Only classes are set here; the motion is in crisus.css (the CSP allows no inline
// style), and prefers-reduced-motion keeps it still.
(function () {
  function spook(mode) {
    if (document.querySelector('.spook')) return;
    var box = document.createElement('div');
    box.className = mode ? 'spook ' + mode : 'spook';
    box.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 5; i++) {
      var c = document.createElement('span');
      c.className = 'munt munt' + i;
      c.textContent = '₿';
      box.appendChild(c);
    }
    var g = document.createElement('span');
    g.className = 'geest';
    g.textContent = '👻';
    var b = document.createElement('span');
    b.className = 'buit';
    b.textContent = '💰';
    g.appendChild(b);
    box.appendChild(g);
    if (mode === 'wiccon') {
      var team = document.createElement('span');
      team.className = 'team';
      team.textContent = '\ud83d\udc69\u200d\ud83d\udcbb\ud83d\udc69\ud83c\udffd\u200d\ud83d\udcbb\ud83d\udc69\ud83c\udfff\u200d\ud83d\udcbb\ud83d\udc69\ud83c\udffc\u200d\ud83d\udcbb';
      box.appendChild(team);
    }
    document.body.appendChild(box);
    setTimeout(function () { box.remove(); }, 7000);
  }
  // The WICCON radar item: whoever keeps it in view for 4 s (at least 90% of it) gets the
  // chase, once per visit. The same on a phone and with a mouse.
  Array.prototype.forEach.call(document.querySelectorAll('ul.radar li > b'), function (b) {
    if (b.textContent !== 'WICCON' || !('IntersectionObserver' in window)) return;
    var seen;
    var watch = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        clearTimeout(seen);
        if (!e.isIntersecting) return;
        seen = setTimeout(function () { watch.disconnect(); spook('wiccon'); }, 4000);
      });
    }, { threshold: 0.9 });
    watch.observe(b.parentNode);
  });
  var typed = '';
  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if (e.ctrlKey || e.metaKey || e.altKey || e.key.length !== 1) return;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    typed = (typed + e.key.toLowerCase()).slice(-7);
    if (/wiccon$/.test(typed)) { typed = ''; spook('wiccon'); }
    else if (/(boe|binance)$/.test(typed)) { typed = ''; spook(); }
  });
  // Three quick clicks on the headline, or on the logo when it links to this very page
  // (one click on that logo still reloads, after a short wait for a second one).
  var h = document.querySelector('h1'), n = 0, timer;
  if (h) h.addEventListener('click', function () {
    n++;
    clearTimeout(timer);
    timer = setTimeout(function () { n = 0; }, 800);
    if (n === 3) { n = 0; spook(); }
  });
  var logo = document.querySelector('a.brand'), clicks = 0, wait;
  if (logo) logo.addEventListener('click', function (e) {
    if (logo.pathname !== location.pathname || e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
    e.preventDefault();
    clicks++;
    clearTimeout(wait);
    if (clicks === 3) { clicks = 0; spook(); return; }
    wait = setTimeout(function () {
      location.href = logo.href;
      clicks = 0;
    }, 600);
  });
})();
