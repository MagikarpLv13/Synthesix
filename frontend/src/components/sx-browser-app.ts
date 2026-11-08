import { LitElement, css, html, nothing, svg, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";

type Profile = { id: string; name: string };
type Result = { title: string; link: string; description?: string; source: string; relevance_score?: number; query_variants?: string[] };
type Request = { queries: string[]; engines: Record<string, boolean>; filters: Record<string, string>; numResults: number; automaticDorks: boolean };
type Coverage = { query: string; engines: Record<string, { status: string; count: number }> };
export type BrowserState = {
  connected: boolean; running: boolean; results: Result[]; profiles: Profile[];
  history: { id: number; created_at: string; count: number; request: Request }[];
  coverage: Coverage[]; status: string; isError: boolean; request?: Request;
};

declare global {
  interface Window {
    synthesixI18n?: { t: (key: string) => string; currentLanguage: () => string; setLanguage: (language: string) => void };
    synthesixTheme?: { setTheme: (theme: string) => void };
  }
}

const ENGINES = [["google", "Google"], ["bing", "Bing"], ["brave", "Brave"], ["duckduckgo", "DuckDuckGo"]] as const;
// Mirrors SearchRequest limits (app/search.py) and the "strong lead" score floor used before the refocus.
const MAX_QUERIES = 20;
const STRONG_SCORE = 8;

@customElement("sx-browser-app")
export class SxBrowserApp extends LitElement {
  @property({ attribute: false }) model: BrowserState = { connected: false, running: false, results: [], profiles: [], history: [], coverage: [], status: "Starting Synthesix...", isError: false };
  @state() private queries = "";
  @state() private engines: Record<string, boolean> = { google: true, bing: true, brave: true, duckduckgo: true };
  @state() private filters: Record<string, string> = {};
  @state() private automatic = true;
  @state() private count = 20;
  @state() private selectedProfile = "";
  @state() private filterText = "";
  @state() private source = "";
  @state() private visible = 100;
  @state() private tab: "search" | "profiles" | "history" = "search";
  @state() private profileName = "";
  private observer = new MutationObserver(() => this.requestUpdate());

  connectedCallback() {
    super.connectedCallback();
    this.observer.observe(document.documentElement, { attributes: true, attributeFilter: ["lang", "data-theme"] });
  }
  disconnectedCallback() { this.observer.disconnect(); super.disconnectedCallback(); }
  protected updated(changes: PropertyValues<this>) {
    const previous = changes.get("model") as BrowserState | undefined;
    if (changes.has("model") && this.model.request && this.model.request !== previous?.request) {
      const request = this.model.request;
      this.queries = request.queries.join("\n"); this.engines = { ...request.engines };
      this.filters = { ...request.filters }; this.automatic = request.automaticDorks;
      this.count = request.numResults; this.tab = "search";
    }
  }
  private t(key: string) { return window.synthesixI18n?.t(key) ?? key; }
  private locale() { return document.documentElement.lang || "fr"; }
  private send(action: string, payload: Record<string, unknown> = {}) {
    this.dispatchEvent(new CustomEvent("sx-browser-action", { detail: { action, ...payload }, bubbles: true, composed: true }));
  }
  private search(event: Event) {
    event.preventDefault(); this.visible = 100; this.filterText = ""; this.source = "";
    this.send("search", { queries: this.queries.split("\n").map(q => q.trim()).filter(Boolean), engines: this.engines, filters: this.filters, numResults: this.count, automaticDorks: this.automatic });
  }
  private field(name: string, label: string, type = "text") {
    return html`<label>${this.t(label)}<input type=${type} name=${name} maxlength="500" autocomplete="off" spellcheck="false" .value=${this.filters[name] ?? ""} @input=${(e: Event) => { this.filters = { ...this.filters, [name]: (e.target as HTMLInputElement).value }; }}></label>`;
  }
  private safeUrl(value: string) {
    try { const u = new URL(value); return ["http:", "https:"].includes(u.protocol) && !u.username && !u.password ? u.href : ""; } catch { return ""; }
  }
  private splitUrl(value: string) {
    try { const u = new URL(value); return { host: u.hostname.replace(/^www\./, ""), path: `${u.pathname === "/" ? "" : u.pathname}${u.search}` }; } catch { return { host: value, path: "" }; }
  }
  private open(event: Event, row: Result) {
    event.preventDefault(); if (this.safeUrl(row.link)) this.send("open_result", { url: row.link, profileId: this.selectedProfile });
  }
  private icon(name: "search" | "sun" | "moon" | "external") {
    const paths = {
      search: svg`<circle cx="7" cy="7" r="4.5"/><path d="m10.5 10.5 3 3"/>`,
      sun: svg`<circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1 1M11.6 11.6l1 1M3.4 12.6l1-1M11.6 4.4l1-1"/>`,
      moon: svg`<path d="M13.5 9.5A5.5 5.5 0 0 1 6.5 2.5a5.5 5.5 0 1 0 7 7Z"/>`,
      external: svg`<path d="M9.5 2.5h4v4M13.5 2.5 8 8M12 9.5v4H2.5V4h4"/>`,
    };
    return html`<svg class="icon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${paths[name]}</svg>`;
  }
  private profileSelect() {
    return html`<label class="profile-picker">${this.t("Open results with")}<select .value=${this.selectedProfile} @change=${(e: Event) => { this.selectedProfile = (e.target as HTMLSelectElement).value; }}><option value="">${this.t("Neutral profile")}</option>${this.model.profiles.map(p => html`<option value=${p.id}>${p.name}</option>`)}</select></label>`;
  }
  private composer() {
    const lines = new Set(this.queries.split("\n").map(q => q.trim()).filter(Boolean)).size;
    const engines = ENGINES.filter(([id]) => this.engines[id]).length;
    const active = Object.values(this.filters).filter(v => v.trim()).length;
    return html`<aside><form @submit=${this.search}>
      <h2>${this.t("Build your search")}</h2>
      <div class="group">
        <div class="label-row"><label for="queries">${this.t("Queries")}</label><span class=${lines > MAX_QUERIES ? "counter over" : "counter"}>${lines} / ${MAX_QUERIES}</span></div>
        <textarea id="queries" name="queries" rows="6" required maxlength="10020" spellcheck="false" autocomplete="off" translate="no" .value=${this.queries} @input=${(e: Event) => { this.queries = (e.target as HTMLTextAreaElement).value; }} placeholder=${this.t("One query per line")}></textarea>
        <label class="check"><input type="checkbox" .checked=${this.automatic} @change=${(e: Event) => { this.automatic = (e.target as HTMLInputElement).checked; }}>${this.t("Automatic exact-phrase dorks")}</label>
      </div>
      <fieldset><legend>${this.t("Search engines")}</legend><div class="engine-grid">${ENGINES.map(([id, label]) => html`<label class="engine"><input type="checkbox" name=${id} .checked=${Boolean(this.engines[id])} @change=${(e: Event) => { this.engines = { ...this.engines, [id]: (e.target as HTMLInputElement).checked }; }}><span translate="no">${label}</span></label>`)}</div></fieldset>
      <details><summary>${this.t("Dork filters")}${active ? html`<span class="badge">${active}</span>` : nothing}</summary><div class="fields">${this.field("site", "Site")}${this.field("exclude", "Exclude")}${this.field("filetype", "File type")}${this.field("title", "Title contains")}${this.field("url", "URL contains")}${this.field("body", "Page contains")}${this.field("country", "Country code")}${this.field("after", "After", "date")}${this.field("before", "Before", "date")}</div></details>
      <label class="count">${this.t("Results per engine")}<input type="number" min="1" max="100" inputmode="numeric" .value=${String(this.count)} @change=${(e: Event) => { this.count = Number((e.target as HTMLInputElement).value); }}></label>
      <div class="submit">
        <p class="plan"><strong>${lines * engines}</strong> ${this.t("engine requests")} <span>(${lines} × ${engines})</span></p>
        <button class="primary" type="submit" ?disabled=${!this.model.connected || this.model.running}>${this.t("Search")}</button>
        ${this.model.running ? html`<button type="button" @click=${() => this.send("cancel_search")}>${this.t("Cancel search")}</button>` : nothing}
      </div>
      <p class="hint">${this.t("Queries are merged into one deduplicated result list.")}</p>
    </form></aside>`;
  }
  private coverage(requested: readonly (readonly [string, string])[], done: number, total: number) {
    const failed = this.model.coverage.reduce((n, row) => n + Object.values(row.engines).filter(e => e.status !== "ok").length, 0);
    return html`<details class="coverage"><summary>${this.t("Search coverage")}<span class="figure">${done} / ${total}</span>${failed ? html`<span class="pill bad">${failed} ${this.t("failed")}</span>` : nothing}</summary>
      <div class="table-wrap"><table><thead><tr><th scope="col">${this.t("Queries")}</th>${requested.map(([, label]) => html`<th scope="col" class="num" translate="no">${label}</th>`)}</tr></thead>
      <tbody>${this.model.coverage.map(c => html`<tr><th scope="row"><code translate="no" title=${c.query}>${c.query}</code></th>${requested.map(([id]) => {
        const item = c.engines[id];
        return html`<td class="num">${!item ? html`<span class="dim">${this.model.running ? "…" : "—"}</span>` : item.status === "ok" ? item.count : html`<span class="pill bad">${this.t(item.status)}</span>`}</td>`;
      })}</tr>`)}</tbody></table></div></details>`;
  }
  private resultRow(row: Result, multiQuery: boolean, format: Intl.NumberFormat) {
    const { host, path } = this.splitUrl(row.link);
    const score = row.relevance_score;
    return html`<article>
      <div class="where" title=${row.link}><span class="host" translate="no">${host}</span><span class="path">${path}</span></div>
      <h2><a href=${this.safeUrl(row.link) || nothing} @click=${(e: Event) => this.open(e, row)}>${row.title || row.link}</a></h2>
      ${score != null ? html`<div class=${score >= STRONG_SCORE ? "score strong" : "score"} title=${this.t("Relevance")}>${format.format(score)}</div>` : nothing}
      ${row.description ? html`<p class="desc">${row.description}</p>` : nothing}
      <div class="meta">${row.source.split(",").map(s => html`<span class="tag" translate="no">${s.trim()}</span>`)}${multiQuery && row.query_variants?.length ? html`<span class="via">${this.t("Found via")}</span>${row.query_variants.map(q => html`<code translate="no">${q}</code>`)}` : nothing}</div>
    </article>`;
  }
  private results() {
    const needle = this.filterText.toLocaleLowerCase();
    const all = this.model.results;
    const matching = all.filter(r => `${r.title} ${r.description ?? ""} ${r.link}`.toLocaleLowerCase().includes(needle));
    const rows = matching.filter(r => !this.source || r.source.toLowerCase().includes(this.source));
    const requested = ENGINES.filter(([id]) => (this.model.request?.engines ?? this.engines)[id]);
    const chips = ENGINES.filter(([id]) => requested.some(([r]) => r === id) || all.some(r => r.source.toLowerCase().includes(id)));
    const done = this.model.coverage.reduce((n, row) => n + Object.keys(row.engines).length, 0);
    const total = this.model.coverage.length * requested.length;
    const format = new Intl.NumberFormat(this.locale(), { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    const multiQuery = (this.model.request?.queries.length ?? 0) > 1;
    return html`<section class="results" aria-busy=${String(this.model.running)}>
      <div class="heading"><div><h1>${this.t("Search results")} <span class="total">${all.length}</span></h1>
        <p class=${this.model.isError ? "status error" : "status"} role="status" aria-live="polite">${this.t(this.model.status)}${total ? html`<span class="progress">${done} / ${total} ${this.t("engine requests completed")}</span>` : nothing}</p></div>
        ${this.profileSelect()}</div>
      ${this.model.running && total ? html`<progress max=${total} .value=${done} aria-label=${this.t("engine requests completed")}></progress>` : nothing}
      ${all.length ? html`<div class="tools"><label class="search-field">${this.icon("search")}<input aria-label=${this.t("Filter results")} placeholder=${this.t("Filter results")} type="search" autocomplete="off" .value=${this.filterText} @input=${(e: Event) => { this.filterText = (e.target as HTMLInputElement).value; this.visible = 100; }}></label><div class="chips" role="group" aria-label=${this.t("Filter by engine")}>${[["", this.t("All engines")] as const, ...chips].map(([id, label]) => html`<button type="button" class="chip" aria-pressed=${String(this.source === id)} @click=${() => { this.source = id; this.visible = 100; }}><span translate="no">${label}</span><span class="n">${id ? matching.filter(r => r.source.toLowerCase().includes(id)).length : matching.length}</span></button>`)}</div></div>` : nothing}
      ${this.model.coverage.length ? this.coverage(requested, done, total) : nothing}
      ${rows.length ? html`<div class="result-list"><div class="list-head" aria-hidden="true">${this.t("Relevance")}</div>${rows.slice(0, this.visible).map(row => this.resultRow(row, multiQuery, format))}</div>${rows.length > this.visible ? html`<button class="more" @click=${() => { this.visible += 100; }}>${this.t("Show more results")}</button>` : nothing}` : html`<div class="empty"><h2>${this.t(all.length ? "No results match this filter." : this.model.running ? "Searching selected engines..." : "Your next search starts here.")}</h2><p>${this.t("Write your queries on the left, choose your engines, then search.")}</p></div>`}
    </section>`;
  }
  private profiles() {
    return html`<section class="secondary"><h1>${this.t("Browser profiles")}</h1><p class="lede">${this.t("Each profile keeps its own website logins. Sign in once in its browser window.")}</p>
      <form class="inline-form" @submit=${(e: Event) => { e.preventDefault(); this.send("create_profile", { name: this.profileName }); this.profileName = ""; }}><label>${this.t("Profile name")}<input required maxlength="80" autocomplete="off" .value=${this.profileName} @input=${(e: Event) => { this.profileName = (e.target as HTMLInputElement).value; }}></label><button class="primary" ?disabled=${!this.model.connected}>${this.t("Create profile")}</button></form>
      <p class=${this.model.isError ? "status error" : "status"} role="status">${this.t(this.model.status)}</p>
      ${this.model.profiles.length ? html`<ul class="rows">${this.model.profiles.map(p => html`<li><form class="profile-row" @submit=${(e: Event) => { e.preventDefault(); const data = new FormData(e.target as HTMLFormElement); this.send("rename_profile", { profileId: p.id, name: data.get("name") }); }}>
        <span class="avatar" style="--hue:${[...p.id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 7)}" aria-hidden="true">${[...p.name.trim()][0]?.toLocaleUpperCase() ?? "?"}</span>
        <label class="sr-only" for=${p.id}>${this.t("Profile name")}</label><input id=${p.id} class="quiet" name="name" .value=${p.name} maxlength="80" required autocomplete="off">
        <button type="submit" ?disabled=${!this.model.connected}>${this.t("Rename")}</button><button type="button" class="with-icon" ?disabled=${!this.model.connected} @click=${() => this.send("open_profile", { profileId: p.id })}>${this.icon("external")}${this.t("Open browser")}</button>
      </form></li>`)}</ul>` : html`<p class="empty-small">${this.t("No browser profiles yet.")}</p>`}
      <p class="hint">${this.t("Profiles separate website sessions. They do not change your IP address.")}</p></section>`;
  }
  private history() {
    const date = new Intl.DateTimeFormat(this.locale(), { dateStyle: "medium", timeStyle: "short" });
    return html`<section class="secondary"><h1>${this.t("Search history")}</h1><p class="lede">${this.t("Reopen saved results or run the same queries again.")}</p>
      ${this.model.history.length ? html`<ul class="rows">${this.model.history.map(run => html`<li><button class="history-row" ?disabled=${this.model.running || !this.model.connected} @click=${() => { this.send("load_search", { id: run.id }); this.tab = "search"; }}>
        <span class="h-main"><span class="h-queries">${run.request.queries.map(q => html`<code translate="no">${q}</code>`)}</span><span class="h-meta"><time datetime=${run.created_at}>${date.format(new Date(run.created_at))}</time><span translate="no">${ENGINES.filter(([id]) => run.request.engines[id]).map(([, label]) => label).join(" · ")}</span></span></span>
        <span class="h-count"><strong>${run.count}</strong> ${this.t("results")}</span></button></li>`)}</ul>` : html`<p class="empty-small">${this.t("No saved searches yet")}</p>`}</section>`;
  }
  render() {
    const dark = document.documentElement.dataset.theme === "dark";
    return html`<div class="shell"><header><a class="brand" href="#" translate="no" @click=${(e: Event) => { e.preventDefault(); this.tab = "search"; }}><img src=${dark ? "assets/synthesix-mark-reversed.svg" : "assets/synthesix-mark.svg"} alt="" width="22" height="22">Synthesix</a><nav aria-label=${this.t("Navigation")}>${([["search", "Search"], ["profiles", "Browser profiles"], ["history", "History"]] as const).map(([id, label]) => html`<button aria-current=${this.tab === id ? "page" : "false"} @click=${() => { this.tab = id; }}>${this.t(label)}</button>`)}</nav><div class="preferences"><label class="sr-only" for="language">${this.t("Language")}</label><select id="language" .value=${window.synthesixI18n?.currentLanguage() ?? "fr"} @change=${(e: Event) => { window.synthesixI18n?.setLanguage((e.target as HTMLSelectElement).value); this.requestUpdate(); }}><option value="fr">Français</option><option value="en">English</option><option value="es">Español</option><option value="pt">Português</option><option value="de">Deutsch</option><option value="zh">中文</option></select><button class="icon-button" title=${this.t("Toggle theme")} aria-label=${this.t("Toggle theme")} @click=${() => window.synthesixTheme?.setTheme(dark ? "light" : "dark")}>${this.icon(dark ? "sun" : "moon")}</button></div></header><div class="workspace">${this.composer()}<main>${this.tab === "search" ? this.results() : this.tab === "profiles" ? this.profiles() : this.history()}</main></div></div>`;
  }

  static styles = css`
    :host { display:block; color:var(--text); font:14px/1.5 var(--font-body); --rule:color-mix(in srgb, var(--line) 65%, transparent); --control-line:var(--border-strong); }
    * { box-sizing:border-box; } h1,h2,p { margin:0; } button,input,textarea,select { font:inherit; color:inherit; }
    button,input,textarea,select { border:1px solid var(--control-line); border-radius:8px; background:var(--field); }
    button { cursor:pointer; padding:0 14px; min-height:36px; font-weight:500; touch-action:manipulation; transition:background-color .12s, border-color .12s; }
    button:hover:not(:disabled) { background:var(--surface-sunken); } button:active:not(:disabled) { transform:translateY(1px); }
    button:disabled { opacity:.55; cursor:not-allowed; } input,select { min-height:36px; padding:0 10px; min-width:0; }
    input:hover,textarea:hover,select:hover { border-color:var(--muted); }
    input:focus-visible,textarea:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible,summary:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
    ::placeholder { color:var(--muted); opacity:.8; }
    .icon { flex:none; display:block; }
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }

    /* Framed sheet: one tinted L (header + composer) around the work sheet, inset 8px right and bottom. */
    .shell { min-height:100vh; background:var(--bg-body); }
    header { height:52px; display:flex; align-items:center; gap:28px; padding:0 16px 0 20px; }
    .brand { font:600 18px var(--font-ui); letter-spacing:-.01em; display:flex; gap:9px; align-items:center; color:var(--text); text-decoration:none; border-radius:6px; }
    nav { display:flex; gap:4px; align-self:stretch; }
    nav button { border:0; border-radius:0; background:none; padding:0 10px; border-bottom:2px solid transparent; color:var(--muted); font-weight:500; }
    nav button:hover:not(:disabled) { background:none; color:var(--text); }
    nav button[aria-current=page] { color:var(--text); border-bottom-color:var(--text); }
    .preferences { margin-left:auto; display:flex; gap:6px; } .preferences select { min-height:32px; border-color:transparent; background:transparent; color:var(--muted); }
    .preferences select:hover { border-color:var(--control-line); color:var(--text); }
    .icon-button { min-height:32px; width:32px; padding:0; display:grid; place-items:center; border-color:transparent; background:transparent; color:var(--muted); }
    .icon-button:hover:not(:disabled) { color:var(--text); }
    .workspace { display:grid; grid-template-columns:304px minmax(0,1fr); gap:8px; padding:0 8px 8px 0; min-height:calc(100vh - 52px); }

    /* Composer */
    aside { padding:12px 20px 24px; } aside form { display:flex; flex-direction:column; gap:20px; }
    aside h2 { font:600 16px var(--font-ui); }
    .group { display:flex; flex-direction:column; gap:8px; }
    label { display:flex; flex-direction:column; gap:6px; font-size:13px; font-weight:500; }
    .label-row { display:flex; justify-content:space-between; align-items:baseline; font-size:13px; font-weight:500; }
    .counter { font-size:12px; font-weight:400; color:var(--muted); font-variant-numeric:tabular-nums; } .counter.over { color:var(--danger); font-weight:600; }
    textarea { padding:10px 12px; resize:vertical; width:100%; min-height:132px; line-height:1.65; font:13px/1.65 var(--font-mono); }
    .check { flex-direction:row; align-items:center; gap:8px; font-weight:400; } .check input { min-height:0; width:15px; height:15px; margin:0; accent-color:var(--accent); }
    fieldset { border:0; padding:0; margin:0; min-width:0; } legend { padding:0 0 8px; font-size:13px; font-weight:500; }
    .engine-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
    .engine { flex-direction:row; align-items:center; gap:8px; min-height:36px; padding:0 10px; border:1px solid var(--control-line); border-radius:8px; background:var(--field); color:var(--muted); font-weight:500; cursor:pointer; transition:border-color .12s, color .12s; }
    .engine input { min-height:0; width:15px; height:15px; margin:0; accent-color:var(--accent); }
    .engine:hover { color:var(--text); } .engine:has(input:checked) { color:var(--text); border-color:color-mix(in srgb, var(--accent) 60%, var(--control-line)); }
    .engine:has(input:focus-visible) { outline:2px solid var(--accent); outline-offset:2px; } .engine input:focus-visible { outline:0; }
    details > summary { cursor:pointer; list-style:none; display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; border-radius:6px; }
    details > summary::-webkit-details-marker { display:none; }
    details > summary::before { content:""; width:6px; height:6px; border:solid currentColor; border-width:0 1.5px 1.5px 0; transform:rotate(-45deg); transition:transform .15s; margin:0 2px 0 1px; opacity:.7; }
    details[open] > summary::before { transform:rotate(45deg); }
    .badge { min-width:20px; height:20px; padding:0 6px; border-radius:999px; display:inline-grid; place-items:center; font-size:12px; background:var(--accent-soft); color:var(--accent-ink); font-variant-numeric:tabular-nums; }
    .fields { display:grid; grid-template-columns:1fr 1fr; gap:12px 8px; padding-top:14px; } .fields label { min-width:0; font-weight:400; }
    .count { flex-direction:row; justify-content:space-between; align-items:center; } .count input { width:72px; text-align:right; font-variant-numeric:tabular-nums; }
    .submit { display:flex; flex-direction:column; gap:8px; padding-top:4px; }
    .plan { font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; } .plan strong { color:var(--text); font-weight:600; }
    button.primary { color:var(--button-primary-text); background:var(--button-primary-bg); border-color:var(--button-primary-bg); min-height:40px; }
    button.primary:hover:not(:disabled) { background:var(--button-primary-bg); filter:brightness(1.18); }
    .hint { font-size:12px; line-height:1.6; color:var(--muted); }

    /* Sheet */
    main { min-width:0; background:var(--surface); border:1px solid var(--line); border-radius:16px; }
    .results,.secondary { padding:28px 32px 32px; } .secondary { max-width:880px; }
    h1 { font:600 22px/1.25 var(--font-ui); letter-spacing:-.01em; }
    .heading { display:flex; justify-content:space-between; gap:24px; align-items:flex-end; }
    .total { font-weight:400; color:var(--muted); margin-left:4px; font-variant-numeric:tabular-nums; }
    .status { font-size:13px; color:var(--muted); margin-top:6px; min-height:20px; } .status.error { color:var(--danger); }
    .progress { font-variant-numeric:tabular-nums; } .status .progress::before { content:"·"; margin:0 6px; }
    .profile-picker { flex:none; width:240px; font-weight:400; color:var(--muted); font-size:12px; } .profile-picker select { color:var(--text); font-size:14px; }
    progress { display:block; width:100%; height:2px; margin-top:16px; border:0; appearance:none; background:var(--surface-sunken); }
    progress::-webkit-progress-bar { background:var(--surface-sunken); } progress::-webkit-progress-value { background:var(--accent); transition:width .2s; }
    .tools { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-top:20px; }
    .search-field { position:relative; flex:1 1 240px; max-width:520px; } .search-field .icon { position:absolute; left:11px; top:50%; transform:translateY(-50%); color:var(--muted); pointer-events:none; }
    .search-field input { width:100%; padding-left:34px; }
    .chips { display:flex; gap:4px; padding:3px; border-radius:10px; background:var(--surface-sunken); overflow-x:auto; scrollbar-width:none; }
    .chip { flex:none; display:inline-flex; align-items:center; gap:7px; min-height:30px; padding:0 10px; border:0; border-radius:7px; background:transparent; color:var(--muted); }
    .chip:hover:not(:disabled) { background:transparent; color:var(--text); }
    .chip[aria-pressed=true] { background:var(--field); color:var(--text); box-shadow:0 0 0 1px var(--line); }
    .chip .n { font-size:12px; font-weight:400; font-variant-numeric:tabular-nums; color:var(--muted); }

    .coverage { margin-top:16px; padding:10px 12px; border-radius:10px; background:var(--surface-sunken); }
    .coverage > summary { font-weight:500; } .figure { font-weight:400; color:var(--muted); font-variant-numeric:tabular-nums; }
    .pill { display:inline-flex; align-items:center; height:20px; padding:0 8px; border-radius:999px; font-size:12px; font-weight:500; white-space:nowrap; flex:none; }
    .pill.bad { background:var(--danger-soft); color:var(--danger-ink); }
    .table-wrap { overflow-x:auto; margin-top:10px; }
    table { width:100%; max-width:760px; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums; }
    th,td { padding:7px 0 7px 16px; text-align:left; border-top:1px solid var(--rule); vertical-align:middle; } th:first-child { padding-left:0; }
    thead th { border-top:0; font-weight:400; color:var(--muted); font-size:12px; padding-top:0; }
    tbody th { font-weight:400; max-width:0; width:55%; } .num { text-align:right; white-space:nowrap; } .dim { color:var(--muted); }
    code { font:12px var(--font-mono); } th code { display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

    .result-list { margin-top:20px; }
    /* Score column on the left of the title: 48px + 20px gap, text keeps one left edge. */
    .list-head { font-size:12px; color:var(--muted); padding-bottom:8px; white-space:nowrap; }
    article { display:grid; grid-template-columns:48px minmax(0,1fr); column-gap:20px; padding:16px 0 18px; border-top:1px solid var(--rule); }
    article > * { grid-column:2; min-width:0; }
    .where { display:flex; min-width:0; font-size:12.5px; white-space:nowrap; } .host { color:var(--text); font-weight:500; flex:none; max-width:100%; overflow:hidden; text-overflow:ellipsis; }
    .path { color:var(--muted); overflow:hidden; text-overflow:ellipsis; }
    article h2 { margin-top:3px; font:500 17px/1.35 var(--font-ui); max-width:78ch; }
    article a { color:var(--accent-link); text-decoration:none; overflow-wrap:anywhere; border-radius:3px; } article a:hover { text-decoration:underline; text-underline-offset:3px; } article a:visited { color:color-mix(in srgb, var(--accent-link) 70%, var(--text)); }
    .score { grid-column:1; grid-row:2; align-self:baseline; text-align:right; font:500 15px var(--font-ui); color:var(--muted); font-variant-numeric:tabular-nums; }
    .score.strong { color:var(--accent); font-weight:700; }
    .desc { margin-top:6px; max-width:78ch; line-height:1.6; overflow-wrap:anywhere; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
    .meta { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin-top:10px; }
    .tag { font-size:12px; font-weight:500; padding:1px 8px; border-radius:5px; background:var(--surface-sunken); color:var(--muted); }
    .via { font-size:12px; color:var(--muted); margin-left:6px; }
    .meta code { padding:1px 6px; border-radius:5px; background:var(--accent-soft); color:var(--accent-ink); overflow-wrap:anywhere; }
    .more { margin-top:16px; }
    .empty { min-height:280px; display:flex; flex-direction:column; justify-content:center; gap:10px; max-width:480px; }
    .empty h2 { font:600 18px var(--font-ui); } .empty p { line-height:1.65; color:var(--muted); }

    /* Profiles and history */
    .lede { margin-top:8px; line-height:1.65; color:var(--muted); max-width:62ch; }
    .inline-form { display:flex; gap:8px; align-items:end; margin:28px 0 0; } .inline-form label { flex:1; max-width:380px; }
    .inline-form button { min-height:36px; }
    .secondary > .status { margin:12px 0 8px; }
    .rows { list-style:none; margin:0; padding:0; } .lede + .rows,.lede + .empty-small { margin-top:24px; }
    .profile-row { display:flex; align-items:center; gap:8px; padding:10px 0; border-top:1px solid var(--rule); }
    .avatar { flex:none; width:32px; height:32px; border-radius:50%; display:grid; place-items:center; font:600 14px var(--font-ui); background:hsl(var(--hue) 42% 88%); color:hsl(var(--hue) 45% 26%); }
    :host-context([data-theme="dark"]) .avatar { background:hsl(var(--hue) 22% 26%); color:hsl(var(--hue) 50% 84%); }
    .quiet { flex:1; border-color:transparent; background:transparent; font-weight:500; } .quiet:hover { border-color:var(--control-line); } .quiet:focus-visible { background:var(--field); }
    .with-icon { display:inline-flex; align-items:center; gap:8px; }
    .empty-small { padding:24px 0; color:var(--muted); border-top:1px solid var(--rule); }
    .secondary > .hint { margin-top:20px; }
    .history-row { display:flex; justify-content:space-between; align-items:center; gap:24px; width:100%; padding:14px 8px; margin:0 -8px; text-align:left; background:none; border:0; border-top:1px solid var(--rule); border-radius:0; font-weight:400; box-sizing:content-box; }
    .history-row:hover:not(:disabled) { background:var(--surface-sunken); }
    .h-main { display:flex; flex-direction:column; gap:6px; min-width:0; } .h-queries { display:flex; flex-wrap:wrap; gap:6px; }
    .h-queries code { padding:2px 7px; border-radius:5px; background:var(--surface-sunken); color:var(--text); overflow-wrap:anywhere; }
    .history-row:hover .h-queries code { background:var(--surface); }
    .h-meta { display:flex; flex-wrap:wrap; gap:4px 12px; font-size:12px; color:var(--muted); }
    .h-count { white-space:nowrap; color:var(--muted); font-variant-numeric:tabular-nums; } .h-count strong { color:var(--text); font-weight:600; }

    @media (prefers-reduced-motion: reduce) { * { transition:none !important; } button:active:not(:disabled) { transform:none; } }
    @media (max-width:1000px) { .workspace { grid-template-columns:272px minmax(0,1fr); } .results,.secondary { padding:24px 20px; } .heading { flex-wrap:wrap; align-items:flex-start; } }
    @media (max-width:680px) {
      header { height:auto; flex-wrap:wrap; gap:4px 12px; padding:10px 12px 0; } .brand { font-size:17px; }
      nav { order:3; width:100%; min-height:42px; } nav button { padding:0 8px; } .preferences select { max-width:110px; }
      .workspace { display:block; padding:0 8px 8px; } aside { padding:16px 8px 24px; } aside form { gap:16px; } textarea { min-height:112px; }
      main { border-radius:12px; } .results,.secondary { padding:20px 14px; } .profile-picker { width:100%; }
      .tools { flex-wrap:wrap; } .search-field { flex-basis:100%; max-width:none; }
      .chips { max-width:100%; } article { grid-template-columns:36px minmax(0,1fr); column-gap:12px; } .score { font-size:14px; }
      .profile-row { flex-wrap:wrap; } .profile-row .quiet { flex-basis:calc(100% - 40px); } .profile-row button { flex:1; justify-content:center; }
      .inline-form { align-items:stretch; flex-direction:column; } .inline-form label { max-width:none; }
      .history-row { flex-direction:column; align-items:flex-start; gap:8px; }
    }
  `;
}
