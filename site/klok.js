// Counts up from the release at 15:34: every minute on it is a minute without
// the update. Without JavaScript it just says 15:34.
(function () {
  var b = document.querySelector('#klok b'), t = Date.UTC(2026, 9, 21, 13, 34, 0);
  function tick() {
    var s = Math.max(0, Math.round((Date.now() - t) / 1000));
    b.textContent = 'patch uit · ' + Math.floor(s / 3600) + ':' + String(Math.floor(s / 60) % 60).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
    setTimeout(tick, 1000);
  }
  tick();
})();
