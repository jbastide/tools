/* Copy for Originals Tools: cookie consent and Google Analytics 4.
   Nothing is loaded from Google until the visitor presses Accept. Consent Mode v2 starts with every
   signal denied; Accept turns on analytics_storage only (no ads signals on this site) and loads gtag.js.
   The choice is kept for 180 days in the first-party cookie cfo_consent on .copyfororiginals.com.
   Squarespace's own ss_performanceCookiesAllowed cookie is host-only on copyfororiginals.com, so the
   tools subdomain can't read it and asks separately.
   Any link to #cookie-settings reopens the banner. Withdrawing consent deletes the _ga cookies on this
   host and on .copyfororiginals.com.
   After Accept, a Content-Security-Policy limits requests to Google Analytics hosts (see lockToAnalytics).
   Pages where visitors type, paste or upload data (the tools, calculators and Script Timer) don't include
   this file and never load Google Analytics; their footer link goes to the homepage's #cookie-settings. */
(function () {
  "use strict";

  var GA_ID = "G-443BVCGXJ1";
  var COOKIE = "cfo_consent";
  var MAX_AGE = 180 * 24 * 60 * 60;
  var PRIVACY = "https://www.copyfororiginals.com/privacy-policy";
  var SITE_DOMAIN = "copyfororiginals.com";

  var sv = (document.documentElement.lang || "").toLowerCase().indexOf("sv") === 0;
  var T = sv ? {
    label: "Cookieinställningar",
    title: "Får vi använda Google Analytics?",
    body: "Med ditt samtycke sätter Google Analytics cookies som visar vilka sidor som läses, så att vi vet vad vi ska skriva härnäst. Inget laddas från Google om du inte godkänner. Du kan ändra dig när som helst via ”Cookieinställningar” längst ned på varje sida.",
    accept: "Godkänn",
    decline: "Neka",
    privacy: "Integritetspolicy",
    current: { granted: "Ditt nuvarande val: godkänt.", denied: "Ditt nuvarande val: nekat." }
  } : {
    label: "Cookie settings",
    title: "Can we use Google Analytics?",
    body: "With your consent, Google Analytics sets cookies that show which pages get read, so we know what to write next. Nothing is loaded from Google unless you accept. You can change your mind any time with “Cookie settings” at the bottom of every page.",
    accept: "Accept",
    decline: "Decline",
    privacy: "Privacy policy",
    current: { granted: "Your current choice: accepted.", denied: "Your current choice: declined." }
  };

  /* Consent Mode v2 defaults, before anything else can run. */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied"
  });

  function onSiteDomain() {
    var h = location.hostname;
    return h === SITE_DOMAIN || h.slice(-(SITE_DOMAIN.length + 1)) === "." + SITE_DOMAIN;
  }

  function readChoice() {
    var m = document.cookie.match(new RegExp("(?:^|;\\s*)" + COOKIE + "=(granted|denied)(?:;|$)"));
    return m ? m[1] : null;
  }

  function writeChoice(value) {
    var c = COOKIE + "=" + value + "; Max-Age=" + MAX_AGE + "; Path=/; SameSite=Lax";
    if (onSiteDomain()) c += "; Domain=." + SITE_DOMAIN;
    if (location.protocol === "https:") c += "; Secure";
    document.cookie = c;
  }

  function deleteGaCookies() {
    var domains = [""];
    if (onSiteDomain()) domains.push("; Domain=" + location.hostname, "; Domain=." + SITE_DOMAIN);
    document.cookie.split(";").forEach(function (part) {
      var name = part.split("=")[0].trim();
      if (!/^(_ga|_ga_.+|_gid|_gat.*)$/.test(name)) return;
      domains.forEach(function (d) {
        document.cookie = name + "=; Max-Age=0; Path=/" + d;
      });
    });
  }

  /* The Google tag G-443BVCGXJ1 also has the Google Ads account as a destination, so gtag.js would send
     an extra page_view to pagead2.googlesyndication.com. Visitors only consent to Google Analytics here,
     so before gtag.js loads this adds a policy that lets requests go to Google Analytics hosts only.
     The pages that load this file have no images, frames or requests of their own beyond 'self'. */
  var GA_HOSTS = "https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com";
  function lockToAnalytics() {
    var meta = document.createElement("meta");
    meta.httpEquiv = "Content-Security-Policy";
    meta.content = "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; " +
      "connect-src 'self' " + GA_HOSTS + "; img-src 'self' data: blob: " + GA_HOSTS + "; frame-src 'none'";
    document.head.appendChild(meta);
  }

  var loaded = false;
  function startAnalytics() {
    window["ga-disable-" + GA_ID] = false;
    gtag("consent", "update", { analytics_storage: "granted" });
    if (loaded) return;
    loaded = true;
    lockToAnalytics();
    gtag("js", new Date());
    /* Referrer without query or fragment: the PPC Gumball Rule calculator keeps the visitor's numbers in
       its URL, and a visitor who clicks through to a page with this file would otherwise send them. */
    gtag("config", GA_ID, { page_referrer: document.referrer.split(/[?#]/)[0] });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }

  function stopAnalytics() {
    gtag("consent", "update", { analytics_storage: "denied" });
    window["ga-disable-" + GA_ID] = true;
    deleteGaCookies();
  }

  function choose(value) {
    var before = readChoice();
    writeChoice(value);
    if (value === "granted") startAnalytics();
    else if (before === "granted" || loaded) stopAnalytics();
    hideBanner();
  }

  /* Banner */
  var banner = null, opener = null;

  function css() {
    var st = document.createElement("style");
    st.textContent =
      ".cfo-consent{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;background:var(--panel,#fff);color:var(--ink,#121212);border-top:3px solid var(--line-strong,#121212);box-shadow:0 -6px 0 var(--accent,#ff5a00);font:16px/1.5 var(--sans,Georgia,serif)}" +
      ".cfo-consent[hidden]{display:none}" +
      ".cfo-consent-in{max-width:760px;margin:0 auto;padding:18px 20px 20px}" +
      ".cfo-consent h2{font:900 22px/1.1 var(--display,Impact,sans-serif);text-transform:uppercase;letter-spacing:.01em;margin:0 0 8px}" +
      ".cfo-consent p{margin:0 0 12px;font-size:15px;color:var(--muted,#4a4842)}" +
      ".cfo-consent p.cfo-now{font-size:14px;color:var(--ink,#121212)}" +
      ".cfo-consent-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 12px}" +
      ".cfo-consent button{flex:0 1 160px;min-width:120px;padding:11px 18px;background:var(--ink,#121212);color:var(--bg,#fafaf6);border:2px solid var(--line-strong,#121212);font:700 15px/1.2 var(--display,Impact,sans-serif);text-transform:uppercase;letter-spacing:.08em;cursor:pointer}" +
      ".cfo-consent button:hover{background:var(--accent,#ff5a00);color:var(--on-accent,#121212)}" +
      ".cfo-consent a{font:700 13px/1.4 var(--display,Impact,sans-serif);text-transform:uppercase;letter-spacing:.1em;margin-left:auto}" +
      "@media (max-width:480px){.cfo-consent-in{padding-inline:16px}.cfo-consent button{flex:1 1 0}.cfo-consent a{margin-left:0}}";
    document.head.appendChild(st);
  }

  function build() {
    css();
    banner = document.createElement("section");
    banner.className = "cfo-consent";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-labelledby", "cfo-consent-title");
    banner.hidden = true;
    banner.innerHTML =
      '<div class="cfo-consent-in">' +
      '<h2 id="cfo-consent-title"></h2><p class="cfo-body"></p><p class="cfo-now" hidden></p>' +
      '<div class="cfo-consent-row">' +
      '<button type="button" data-choice="granted"></button>' +
      '<button type="button" data-choice="denied"></button>' +
      '<a rel="noopener"></a></div></div>';
    banner.querySelector("h2").textContent = T.title;
    banner.querySelector(".cfo-body").textContent = T.body;
    banner.querySelector('[data-choice="granted"]').textContent = T.accept;
    banner.querySelector('[data-choice="denied"]').textContent = T.decline;
    var a = banner.querySelector("a");
    a.href = PRIVACY;
    a.textContent = T.privacy;
    banner.addEventListener("click", function (e) {
      var b = e.target.closest("[data-choice]");
      if (b) choose(b.getAttribute("data-choice"));
    });
    banner.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && readChoice()) hideBanner();
    });
    document.body.appendChild(banner);
  }

  function showBanner(focus) {
    if (!banner) build();
    var now = banner.querySelector(".cfo-now"), c = readChoice();
    now.hidden = !c;
    now.textContent = c ? T.current[c] : "";
    banner.hidden = false;
    if (focus) {
      opener = document.activeElement;
      banner.querySelector("button").focus();
    }
  }

  function hideBanner() {
    if (!banner) return;
    banner.hidden = true;
    if (opener && opener.focus) opener.focus();
    opener = null;
  }

  function openFromLink(e) {
    var a = e.target.closest && e.target.closest('a[href$="#cookie-settings"]');
    if (!a) return;
    e.preventDefault();
    showBanner(true);
  }

  var choice = readChoice();
  if (choice === "granted") startAnalytics();

  function init() {
    document.addEventListener("click", openFromLink);
    if (location.hash === "#cookie-settings") {
      history.replaceState(null, "", location.pathname + location.search);
      showBanner(true);
    } else if (!choice) {
      showBanner(false);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
