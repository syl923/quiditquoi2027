function main(D) {
  const page = document.body.dataset.page;

  // ---------- Helpers ----------
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const $ = (sel) => document.querySelector(sel);
  const fmtDate = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
  const candById = (id) => D.candidats.find((c) => c.id === id);
  const themeById = (id) => D.themes.find((t) => t.id === id);
  const initials = (nom) => nom.split(/\s+/).map((p) => p[0]).slice(0, 2).join("").toUpperCase();
  const byDateDesc = (a, b) => b.date.localeCompare(a.date);
  const STATUTS = { declare: "Candidature déclarée", primaire: "En primaire", pressenti: "Pressenti", retire: "Retiré" };
  const posOf = (cid, tid) => D.positions.filter((p) => p.candidat === cid && p.theme === tid);
  const sourceLink = (src, label = "Source") => `<a class="source-link" href="${esc(src.url)}" target="_blank" rel="noopener nofollow">${label} : ${esc(src.titre)} ↗</a>`;

  const avatar = (c, cls = "") =>
    `<div class="avatar ${cls}" style="--c:${esc(c.couleur)}">${c.photo ? `<img src="${esc(c.photo.fichier)}" alt="${esc(c.nom)}" loading="lazy">` : esc(initials(c.nom))}</div>`;
  const exempleBadge = (x) => (x.exemple ? `<span class="badge exemple">Exemple</span>` : "");

  // ---------- Layout ----------
  const NAV = [
    ["index.html", "Accueil", "accueil"],
    ["candidats.html", "Candidats", "candidats"],
    ["declarations.html", "Déclarations", "declarations"],
    ["programmes.html", "Programmes", "programmes"],
    ["comparateur.html", "Comparateur", "comparateur"],
    ["calendrier.html", "Calendrier", "calendrier"]
  ];

  function renderLayout() {
    const hasDemo = [...D.candidats, ...D.declarations, ...D.positions].some((x) => x.exemple);
    $("#site-header").outerHTML = `
      <header class="site-header">
        <div class="container">
          <a class="logo" href="index.html">Qui dit quoi <span class="logo-badge">2027</span></a>
          <nav class="nav">
            ${NAV.map(([href, label, id]) => `<a href="${href}" class="${page === id || (page === "candidat" && id === "candidats") ? "active" : ""}">${label}</a>`).join("")}
          </nav>
        </div>
      </header>
      ${hasDemo ? `<div class="demo-banner">⚠️ Site en construction : les candidats et déclarations affichés sont des <strong>données d'exemple</strong>.</div>` : ""}`;

    $("#site-footer").outerHTML = `
      <footer class="site-footer">
        <div class="container">
          <span>© ${new Date().getFullYear()} Qui dit quoi 2027 — site indépendant, sans affiliation politique.${D.majLe ? ` Données mises à jour le ${fmtDate(D.majLe)}.` : ""}</span>
          <span><a href="a-propos.html">Méthodologie &amp; mentions</a></span>
        </div>
      </footer>`;
  }

  // ---------- Components ----------
  function candCard(c) {
    const n = D.declarations.filter((d) => d.candidat === c.id).length;
    return `
      <a class="card cand-card" href="candidat.html?id=${encodeURIComponent(c.id)}" style="--c:${esc(c.couleur)}">
        ${avatar(c)}
        <h3>${esc(c.nom)}</h3>
        <div class="parti">${esc(c.parti)}</div>
        <div class="badges">
          <span class="badge ${esc(c.statut)}">${STATUTS[c.statut] || esc(c.statut)}</span>
          <span class="badge">${n} déclaration${n > 1 ? "s" : ""}</span>
          ${exempleBadge(c)}
        </div>
      </a>`;
  }

  function declCard(d) {
    const c = candById(d.candidat);
    const t = themeById(d.theme);
    if (!c) return "";
    return `
      <article class="card decl" style="--c:${esc(c.couleur)}">
        <div class="decl-top">
          ${avatar(c)}
          <div>
            <a class="decl-who" href="candidat.html?id=${encodeURIComponent(c.id)}">${esc(c.nom)}</a>
            <div class="decl-meta">${fmtDate(d.date)}${d.contexte ? " · " + esc(d.contexte) : ""}</div>
          </div>
        </div>
        <blockquote>${esc(d.texte)}</blockquote>
        <div class="decl-foot">
          <div class="badges" style="margin:0">
            ${t ? `<span class="badge">${t.emoji} ${esc(t.nom)}</span>` : ""}
            ${exempleBadge(d)}
          </div>
          <a class="source-link" href="${esc(d.source.url)}" target="_blank" rel="noopener nofollow">Source : ${esc(d.source.titre)} ↗</a>
        </div>
      </article>`;
  }

  // ---------- Pages ----------
  function pageAccueil() {
    const target = new Date(D.election.premierTour + "T08:00:00");
    const units = [["j", "jours", 86400000], ["h", "heures", 3600000], ["m", "minutes", 60000], ["s", "secondes", 1000]];
    $("#countdown").innerHTML = units.map(([k, l]) => `<div class="unit"><span class="num" data-u="${k}">–</span><span class="lbl">${l}</span></div>`).join("");
    $("#countdown-note").textContent = `Premier tour : ${fmtDate(D.election.premierTour)}${D.election.datesConfirmees ? "" : " (date prévisionnelle, à confirmer)"}`;
    const tick = () => {
      let ms = Math.max(0, target - new Date());
      units.forEach(([k, , size]) => {
        const v = Math.floor(ms / size);
        ms -= v * size;
        document.querySelector(`[data-u="${k}"]`).textContent = k === "j" ? v : String(v).padStart(2, "0");
      });
    };
    tick();
    setInterval(tick, 1000);

    $("#latest").innerHTML = [...D.declarations].sort(byDateDesc).slice(0, 4).map(declCard).join("") || `<p class="empty">Aucune déclaration pour l'instant.</p>`;
    $("#cands").innerHTML = D.candidats.filter((c) => c.statut === "declare").map(candCard).join("");
  }

  function pageCandidats() {
    const groups = [["declare", "Candidats déclarés"], ["primaire", "Candidats à une primaire"], ["pressenti", "Pressentis"], ["retire", "Retirés"]];
    $("#groups").innerHTML = groups
      .map(([s, title]) => {
        const list = D.candidats.filter((c) => c.statut === s);
        return list.length ? `<section class="section"><div class="section-head"><h2>${title}</h2></div><div class="grid">${list.map(candCard).join("")}</div></section>` : "";
      })
      .join("");
  }

  function pageCandidat() {
    const id = new URLSearchParams(location.search).get("id");
    const c = candById(id);
    if (!c) {
      $("#profile").innerHTML = `<p class="empty">Candidat introuvable. <a href="candidats.html">Voir tous les candidats</a></p>`;
      return;
    }
    document.title = `${c.nom} — Qui dit quoi 2027`;
    const canon = document.createElement("link");
    canon.rel = "canonical";
    canon.href = `${location.origin}/candidat.html?id=${encodeURIComponent(c.id)}`;
    document.head.appendChild(canon);
    const desc = document.querySelector('meta[name="description"]');
    if (desc) desc.content = `${c.nom} (${c.parti}) : déclarations sourcées et positions pour la présidentielle 2027.`;
    $("#profile").innerHTML = `
      <div class="profile" style="--c:${esc(c.couleur)}">
        ${avatar(c, "lg")}
        <div>
          <h1>${esc(c.nom)}</h1>
          <div class="parti">${esc(c.parti)}</div>
          <div class="badges">
            <span class="badge ${esc(c.statut)}">${STATUTS[c.statut] || esc(c.statut)}</span>
            ${c.dateDeclaration ? `<span class="badge">Déclaré le ${fmtDate(c.dateDeclaration)}</span>` : ""}
            ${exempleBadge(c)}
          </div>
        </div>
      </div>
      <p class="page-intro">${esc(c.bio)}${c.source ? `<br>${sourceLink(c.source)}` : ""}</p>
      ${c.photo ? `<p class="photo-credit">Photo : <a href="${esc(c.photo.url)}" target="_blank" rel="noopener">${esc(c.photo.credit)}</a>, via Wikimedia Commons</p>` : ""}`;

    const pos = D.positions.filter((p) => p.candidat === c.id);
    $("#positions").innerHTML = pos.length
      ? pos.map((p) => {
          const t = themeById(p.theme);
          return `<div class="card pos-card" style="--c:${esc(c.couleur)}"><h3 style="margin-top:0">${t ? t.emoji + " " + esc(t.nom) : ""}</h3><p>${esc(p.resume)}</p>${sourceLink(p.source)}</div>`;
        }).join("")
      : `<p class="empty">Aucune position renseignée.</p>`;

    const decls = D.declarations.filter((d) => d.candidat === c.id).sort(byDateDesc);
    $("#decls").innerHTML = decls.map(declCard).join("") || `<p class="empty">Aucune déclaration pour l'instant.</p>`;
  }

  function pageDeclarations() {
    const state = { cand: "", theme: "" };
    $("#f-cand").innerHTML = `<option value="">Tous les candidats</option>` + D.candidats.map((c) => `<option value="${esc(c.id)}">${esc(c.nom)}</option>`).join("");
    $("#f-theme").innerHTML = `<option value="">Tous les thèmes</option>` + D.themes.map((t) => `<option value="${esc(t.id)}">${t.emoji} ${esc(t.nom)}</option>`).join("");
    const render = () => {
      const list = D.declarations.filter((d) => (!state.cand || d.candidat === state.cand) && (!state.theme || d.theme === state.theme)).sort(byDateDesc);
      $("#list").innerHTML = list.map(declCard).join("") || `<p class="empty">Aucune déclaration ne correspond à ces filtres.</p>`;
    };
    $("#f-cand").addEventListener("change", (e) => { state.cand = e.target.value; render(); });
    $("#f-theme").addEventListener("change", (e) => { state.theme = e.target.value; render(); });
    render();
  }

  function pageComparateur() {
    const themes = D.themes.filter((t) => t.id !== "campagne");
    let current = new URLSearchParams(location.search).get("theme") || themes[0].id;
    const render = () => {
      $("#tabs").innerHTML = themes.map((t) => `<button class="chip ${t.id === current ? "on" : ""}" data-t="${esc(t.id)}">${t.emoji} ${esc(t.nom)}</button>`).join("");
      $("#compare").innerHTML = D.candidats
        .filter((c) => c.statut !== "retire")
        .map((c) => {
          const ps = posOf(c.id, current);
          return `
            <div class="card pos-card" style="--c:${esc(c.couleur)}">
              <div class="who">${avatar(c)}<div><strong>${esc(c.nom)}</strong><div class="decl-meta">${esc(c.parti)}</div></div></div>
              ${ps.length ? ps.map((p) => `<p>${esc(p.resume)}</p>${sourceLink(p.source)}`).join("") : `<p class="pos-empty">Pas encore de position connue sur ce thème.</p>`}
            </div>`;
        })
        .join("");
    };
    $("#tabs").addEventListener("click", (e) => {
      const b = e.target.closest("[data-t]");
      if (!b) return;
      current = b.dataset.t;
      history.replaceState(null, "", "?theme=" + current);
      render();
    });
    render();
  }

  function pageCalendrier() {
    const today = new Date().toISOString().slice(0, 10);
    $("#timeline").innerHTML = [...D.calendrier]
      .sort((a, b) => a.date.localeCompare(b.date))
      .map((e) => `
        <div class="tl-item ${e.date < today ? "past" : ""}">
          <div class="card">
            <div class="tl-date">${fmtDate(e.date)}</div>
            <h3 style="margin:4px 0">${esc(e.titre)}</h3>
            <div class="decl-meta">${esc(e.description)}</div>
            ${e.confirme ? "" : `<div class="badges"><span class="badge pressenti">À confirmer</span></div>`}
            ${e.source ? `<div class="decl-meta" style="margin-top:8px">${sourceLink(e.source)}</div>` : ""}
          </div>
        </div>`)
      .join("");
  }

  function pageProgrammes() {
    const themes = D.themes.filter((t) => t.principal);
    const cands = D.candidats.filter((c) => D.positions.some((p) => p.candidat === c.id && themes.some((t) => t.id === p.theme)));
    $("#syntheses").innerHTML = themes.map((t) => `
      <div class="card synth">
        <h3>${t.emoji} ${esc(t.nom)}</h3>
        <p>${esc((D.syntheses || {})[t.id] || "")}</p>
      </div>`).join("");
    $("#prog-table").innerHTML = `
      <thead><tr><th>Candidat</th>${themes.map((t) => `<th>${t.emoji} ${esc(t.nom)}</th>`).join("")}</tr></thead>
      <tbody>${cands.map((c) => `
        <tr style="--c:${esc(c.couleur)}">
          <th scope="row"><a class="prog-cand" href="candidat.html?id=${encodeURIComponent(c.id)}">${avatar(c)}<span><strong>${esc(c.nom)}</strong><small>${esc(c.parti)}</small></span></a></th>
          ${themes.map((t) => {
            const ps = posOf(c.id, t.id);
            return `<td>${ps.length ? `<ul>${ps.map((p) => `<li>${esc(p.resume)} <a class="src" href="${esc(p.source.url)}" target="_blank" rel="noopener nofollow" title="${esc(p.source.titre)}">[source]</a></li>`).join("")}</ul>` : `<span class="pos-empty">Pas encore de position sourcée</span>`}</td>`;
          }).join("")}
        </tr>`).join("")}
      </tbody>`;
  }

  renderLayout();
  ({ accueil: pageAccueil, candidats: pageCandidats, candidat: pageCandidat, declarations: pageDeclarations, comparateur: pageComparateur, programmes: pageProgrammes, calendrier: pageCalendrier }[page] || (() => {}))();
}

// Charge data/data.json, remplace les clés de source par l'objet source correspondant, puis affiche la page.
fetch("data/data.json", { cache: "no-cache" })
  .then((r) => r.json())
  .then((D) => {
    const resolve = (x) => { if (x && typeof x.source === "string") x.source = D.sources[x.source] || { titre: "Source inconnue", url: "#" }; };
    [D.election, ...D.candidats, ...D.declarations, ...D.positions, ...D.calendrier].forEach(resolve);
    main(D);
  })
  .catch((e) => {
    document.querySelector("main").insertAdjacentHTML("afterbegin", '<p class="empty">Impossible de charger les données. Réessayez plus tard.</p>');
    console.error(e);
  });
