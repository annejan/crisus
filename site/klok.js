// Counts up from the release at 15:34, in days and hh:mm:ss: every minute on it
// is a minute without the update. Without JavaScript it just says 15:34.
(function () {
  var b = document.querySelector('#klok b'), t = Date.UTC(2026, 9, 21, 13, 34, 0);
  function tick() {
    var s = Math.max(0, Math.round((Date.now() - t) / 1000));
    var d = Math.floor(s / 86400), hms = [Math.floor(s / 3600) % 24, Math.floor(s / 60) % 60, s % 60]
      .map(function (n) { return String(n).padStart(2, '0'); }).join(':');
    b.textContent = (d ? d + (d === 1 ? ' dag ' : ' dagen ') : '') + hms;
    setTimeout(tick, 1000);
  }
  tick();
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
