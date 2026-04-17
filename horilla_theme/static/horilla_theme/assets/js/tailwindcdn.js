/**
 * Tailwind JIT/play CDN for arbitrary classes (e.g. bg-[#f8f8f9]) in templates.
 * Precompiled tailwind.css alone does not include all arbitrary utilities.
 */
(function () {
  var s = document.createElement("script");
  s.src = "https://cdn.tailwindcss.com";
  s.crossOrigin = "anonymous";
  document.head.appendChild(s);
})();
