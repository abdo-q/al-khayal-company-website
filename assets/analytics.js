/* Set the real GA4 ID in the data-ga-id attribute on the script tag. */
(function () {
  var script = document.currentScript;
  var measurementId = script && script.dataset.gaId;
  if (!measurementId || !/^G-[A-Z0-9]+$/i.test(measurementId)) return;
  window.dataLayer = window.dataLayer || [];
  function gtag(){ window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", measurementId);
  var external = document.createElement("script");
  external.async = true;
  external.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
  document.head.appendChild(external);
})();
