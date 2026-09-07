/* Framing guard: in a frame, this page renders nothing. Loaded first, by the
   pages that name it; the rest of the site is embeddable and stays so. */
(function () {
  var framed;
  try {
    framed = window.top !== window.self;
  } catch (e) {
    framed = true;
  }
  if (!framed) return;
  // Nothing paints, nothing is clickable, and this navigates nowhere.
  try {
    document.documentElement.style.display = 'none';
  } catch (e) { /* the stop below is the other half */ }
  // Stop parsing: the rest of the document, the stylesheet and the runtime are
  // never fetched.
  try {
    window.stop();
  } catch (e) { /* the page stays hidden either way */ }
})();
