import { LitElement, css, html, type PropertyValues } from "lit";
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
  private send(action: string, payload: Record<string, unknown> = {}) {
    this.dispatchEvent(new CustomEvent("sx-browser-action", { detail: { action, ...payload }, bubbles: true, composed: true }));
  }
  private search(event: Event) {
    event.preventDefault(); this.visible = 100; this.filterText = ""; this.source = "";
    this.send("search", { queries: this.queries.split("\n").map(q => q.trim()).filter(Boolean), engines: this.engines, filters: this.filters, numResults: this.count, automaticDorks: this.automatic });
  }
  private field(name: string, label: string, type = "text") {
    return html`<label>${this.t(label)}<input type=${type} name=${name} maxlength="500" .value=${this.filters[name] ?? ""} @input=${(e: Event) => { this.filters = { ...this.filters, [name]: (e.target as HTMLInputElement).value }; }}></label>`;
  }
  private safeUrl(value: string) {
    try { const u = new URL(value); return ["http:", "https:"].includes(u.protocol) && !u.username && !u.password ? u.href : ""; } catch { return ""; }
  }
  private open(event: Event, row: Result) {
    event.preventDefault(); if (this.safeUrl(row.link)) this.send("open_result", { url: row.link, profileId: this.selectedProfile });
  }
  private profileSelect() {
    return html`<label class="profile-picker">${this.t("Open results with")}<select aria-label=${this.t("Open results with")} .value=${this.selectedProfile} @change=${(e: Event) => { this.selectedProfile = (e.target as HTMLSelectElement).value; }}><option value="">${this.t("Neutral profile")}</option>${this.model.profiles.map(p => html`<option value=${p.id}>${p.name}</option>`)}</select></label>`;
  }
  private composer() {
    return html`<aside><form @submit=${this.search}>
      <h2>${this.t("Build your search")}</h2>
      <label for="queries">${this.t("Queries")}</label>
      <textarea id="queries" name="queries" rows="6" required maxlength="10020" spellcheck="false" .value=${this.queries} @input=${(e: Event) => { this.queries = (e.target as HTMLTextAreaElement).value; }} placeholder=${this.t("One query per line")}></textarea>
      <label class="check"><input type="checkbox" .checked=${this.automatic} @change=${(e: Event) => { this.automatic = (e.target as HTMLInputElement).checked; }}>${this.t("Automatic exact-phrase dorks")}</label>
      <fieldset><legend>${this.t("Search engines")}</legend><div class="engine-grid">${[["google", "Google"], ["bing", "Bing"], ["brave", "Brave"], ["duckduckgo", "DuckDuckGo"]].map(([id, label]) => html`<label class="check"><input type="checkbox" name=${id} .checked=${Boolean(this.engines[id])} @change=${(e: Event) => { this.engines = { ...this.engines, [id]: (e.target as HTMLInputElement).checked }; }}>${label}</label>`)}</div></fieldset>
      <details><summary>${this.t("Dork filters")}</summary><div class="fields">${this.field("site", "Site")}${this.field("exclude", "Exclude")}${this.field("filetype", "File type")}${this.field("title", "Title contains")}${this.field("url", "URL contains")}${this.field("body", "Page contains")}${this.field("country", "Country code")}${this.field("after", "After", "date")}${this.field("before", "Before", "date")}</div></details>
      <label class="count">${this.t("Results per engine")}<input type="number" min="1" max="100" .value=${String(this.count)} @change=${(e: Event) => { this.count = Number((e.target as HTMLInputElement).value); }}></label>
      <button class="primary" type="submit" ?disabled=${!this.model.connected || this.model.running}>${this.t("Search")}</button>
      ${this.model.running ? html`<button type="button" @click=${() => this.send("cancel_search")}>${this.t("Cancel search")}</button>` : ""}
      <p class="muted hint">${this.t("Queries are merged into one deduplicated result list.")}</p>
    </form></aside>`;
  }
  private results() {
    const needle = this.filterText.toLocaleLowerCase();
    const rows = this.model.results.filter(r => (!this.source || r.source.toLowerCase().includes(this.source)) && `${r.title} ${r.description ?? ""} ${r.link}`.toLocaleLowerCase().includes(needle));
    const complete = this.model.coverage.reduce((n, row) => n + Object.keys(row.engines).length, 0);
    const total = this.model.coverage.length * Object.values(this.model.request?.engines ?? this.engines).filter(Boolean).length;
    return html`<section class="results" aria-busy=${String(this.model.running)}><div class="heading"><div><h1>${this.t("Search results")} <span class="total">${rows.length}</span></h1>${total ? html`<p class="muted progress">${complete} / ${total} ${this.t("engine requests completed")}</p>` : ""}</div>${this.profileSelect()}</div>
      <div class="tools"><input aria-label=${this.t("Filter results")} placeholder=${this.t("Filter results")} type="search" .value=${this.filterText} @input=${(e: Event) => { this.filterText = (e.target as HTMLInputElement).value; this.visible = 100; }}><select aria-label=${this.t("Search engines")} .value=${this.source} @change=${(e: Event) => { this.source = (e.target as HTMLSelectElement).value; }}><option value="">${this.t("All engines")}</option>${["Google", "Bing", "Brave", "DuckDuckGo"].map(s => html`<option value=${s.toLowerCase()}>${s}</option>`)}</select></div>
      <p class=${this.model.isError ? "status error" : "status"} role="status" aria-live="polite">${this.t(this.model.status)}</p>
      ${this.model.coverage.some(c => Object.values(c.engines).some(e => e.status !== "ok")) ? html`<details class="coverage"><summary>${this.t("Search coverage")}</summary>${this.model.coverage.map(c => html`<div class="coverage-row"><code>${c.query}</code><span>${Object.entries(c.engines).map(([engine, item]) => html`<span class=${item.status === "ok" ? "" : "error"}>${engine}: ${this.t(item.status)} (${item.count}) </span>`)}</span></div>`)}</details>` : ""}
      ${rows.length ? html`<div class="result-list">${rows.slice(0, this.visible).map(row => html`<article><div class="result-source"><span>${row.source}</span>${row.relevance_score != null ? html`<span title=${this.t("Relevance")}>${row.relevance_score.toFixed(1)}</span>` : ""}</div><h2><a href=${this.safeUrl(row.link) || undefined} @click=${(e: Event) => this.open(e, row)}>${row.title || row.link}</a></h2><div class="url">${row.link}</div>${row.description ? html`<p>${row.description}</p>` : ""}${row.query_variants?.length ? html`<div class="found-via">${this.t("Found via")} ${row.query_variants.join(" · ")}</div>` : ""}</article>`)}</div>${rows.length > this.visible ? html`<button class="more" @click=${() => { this.visible += 100; }}>${this.t("Show more results")}</button>` : ""}` : html`<div class="empty"><h2>${this.t(this.model.results.length ? "No results match this filter." : this.model.running ? "Searching selected engines..." : "Your next search starts here.")}</h2><p>${this.t("Write your queries on the left, choose your engines, then search.")}</p></div>`}
    </section>`;
  }
  private profiles() {
    return html`<section class="secondary"><h1>${this.t("Browser profiles")}</h1><p class="muted">${this.t("Each profile keeps its own website logins. Sign in once in its browser window.")}</p><form class="inline-form" @submit=${(e: Event) => { e.preventDefault(); this.send("create_profile", { name: this.profileName }); this.profileName = ""; }}><label>${this.t("Profile name")}<input required maxlength="80" .value=${this.profileName} @input=${(e: Event) => { this.profileName = (e.target as HTMLInputElement).value; }}></label><button class="primary" ?disabled=${!this.model.connected}>${this.t("Create profile")}</button></form><p class="status" role="status">${this.t(this.model.status)}</p>
      ${this.model.profiles.map(p => html`<form class="profile-row" @submit=${(e: Event) => { e.preventDefault(); const data = new FormData(e.target as HTMLFormElement); this.send("rename_profile", { profileId: p.id, name: data.get("name") }); }}><label class="sr-only" for=${p.id}>${this.t("Profile name")}</label><input id=${p.id} name="name" .value=${p.name} maxlength="80" required><button type="submit" ?disabled=${!this.model.connected}>${this.t("Rename")}</button><button type="button" ?disabled=${!this.model.connected} @click=${() => this.send("open_profile", { profileId: p.id })}>${this.t("Open browser")}</button></form>`)}
      ${!this.model.profiles.length ? html`<p class="empty-small">${this.t("No browser profiles yet.")}</p>` : ""}<p class="muted hint">${this.t("Profiles separate website sessions. They do not change your IP address.")}</p></section>`;
  }
  private history() {
    return html`<section class="secondary"><h1>${this.t("Search history")}</h1><p class="muted">${this.t("Reopen saved results or run the same queries again.")}</p>${this.model.history.length ? this.model.history.map(run => html`<button class="history-row" ?disabled=${this.model.running || !this.model.connected} @click=${() => { this.send("load_search", { id: run.id }); this.tab = "search"; }}><span><strong>${run.request.queries.join(" · ")}</strong><time>${new Date(run.created_at).toLocaleString(document.documentElement.lang)}</time></span><span>${run.count} ${this.t("results")}</span></button>`) : html`<p class="empty-small">${this.t("No saved searches yet")}</p>`}</section>`;
  }
  render() {
    return html`<div class="shell"><header><a class="brand" href="#" @click=${(e: Event) => { e.preventDefault(); this.tab = "search"; }}><img src=${document.documentElement.dataset.theme === "dark" ? "assets/synthesix-mark-reversed.svg" : "assets/synthesix-mark.svg"} alt="" width="25" height="25">Synthesix</a><nav aria-label=${this.t("Navigation")}>${([["search", "Search"], ["profiles", "Browser profiles"], ["history", "History"]] as const).map(([id, label]) => html`<button aria-current=${this.tab === id ? "page" : "false"} @click=${() => { this.tab = id; }}>${this.t(label)}</button>`)}</nav><div class="preferences"><label class="sr-only" for="language">${this.t("Language")}</label><select id="language" .value=${window.synthesixI18n?.currentLanguage() ?? "fr"} @change=${(e: Event) => { window.synthesixI18n?.setLanguage((e.target as HTMLSelectElement).value); this.requestUpdate(); }}><option value="fr">Français</option><option value="en">English</option><option value="es">Español</option><option value="pt">Português</option><option value="de">Deutsch</option><option value="zh">中文</option></select><button title=${this.t("Toggle theme")} aria-label=${this.t("Toggle theme")} @click=${() => window.synthesixTheme?.setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark")}>◐</button></div></header><div class="workspace">${this.composer()}<main>${this.tab === "search" ? this.results() : this.tab === "profiles" ? this.profiles() : this.history()}</main></div></div>`;
  }

  static styles = css`
    :host { display:block; color:var(--text); font:14px var(--font-body); }
    * { box-sizing:border-box; } button,input,textarea,select { font:inherit; color:inherit; }
    button,input,textarea,select { border:1px solid var(--line); border-radius:6px; background:var(--field); }
    button { cursor:pointer; padding:8px 12px; min-height:36px; } button:hover:not(:disabled) { background:var(--surface-sunken); }
    button:disabled { opacity:.5; cursor:default; } input,select { min-height:36px; padding:7px 9px; min-width:0; }
    input:focus-visible,textarea:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible,summary:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
    .shell { min-height:100vh; background:var(--bg-body); } header { min-height:56px; display:flex; align-items:center; gap:24px; padding:0 20px; }
    .brand { font:600 20px var(--font-ui); display:flex; gap:9px; align-items:center; color:var(--text); text-decoration:none; } nav { display:flex; gap:8px; align-self:stretch; }
    nav button { border:0; border-radius:0; background:none; padding:0 10px; border-bottom:2px solid transparent; color:var(--muted); } nav button[aria-current=page] { color:var(--text); border-bottom-color:var(--accent); }
    .preferences { margin-left:auto; display:flex; gap:8px; } .preferences button { font-size:20px; padding:2px 10px; }
    /* 304px composer + flexible sheet; 8px outer inset, no unused right column. */
    .workspace { display:grid; grid-template-columns:304px minmax(0,1fr); gap:8px; padding:0 8px 8px 0; min-height:calc(100vh - 56px); }
    aside { padding:20px; } aside form { display:flex; flex-direction:column; gap:16px; } h1,h2,p { margin:0; } h1 { font:600 24px var(--font-ui); } h2 { font:600 16px var(--font-ui); } aside h2 { margin-bottom:4px; }
    label { display:flex; flex-direction:column; gap:7px; font-size:13px; } textarea { padding:10px; resize:vertical; width:100%; min-height:130px; line-height:1.6; font-family:var(--font-mono); }
    .check { display:flex; flex-direction:row; align-items:center; gap:8px; line-height:1.5; } .check input { min-height:0; width:15px; height:15px; margin:0; accent-color:var(--accent); }
    fieldset { border:0; padding:0; margin:0; } legend { padding:0 0 12px; font-size:13px; } .engine-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px 4px; }
    summary { cursor:pointer; font-weight:600; padding:4px 0; } .fields { display:grid; grid-template-columns:1fr 1fr; gap:12px 8px; padding-top:14px; } .fields label { min-width:0; }
    .count { flex-direction:row; justify-content:space-between; align-items:center; } .count input { width:70px; }
    button.primary { color:var(--button-primary-text); background:var(--button-primary-bg); border-color:var(--button-primary-bg); } button.primary:hover:not(:disabled) { filter:brightness(.9); }
    main { min-width:0; background:var(--surface); border:1px solid var(--line); border-radius:16px; } .results,.secondary { padding:24px 28px; } .secondary { max-width:960px; }
    .heading { display:flex; justify-content:space-between; gap:20px; align-items:flex-start; } .total { font-variant-numeric:tabular-nums; font-weight:400; color:var(--muted); margin-left:6px; }
    .profile-picker { max-width:250px; min-width:160px; } .muted,.hint,.url,.found-via { color:var(--muted); } .hint { font-size:12px; line-height:1.65; } .progress { font-size:12px; margin-top:6px; }
    .tools { display:flex; gap:8px; margin-top:22px; } .tools input { flex:1; max-width:600px; } .tools select { max-width:170px; }
    .status { min-height:20px; font-size:13px; margin:16px 0; } .error { color:var(--danger); } .empty { min-height:220px; display:flex; flex-direction:column; justify-content:center; gap:12px; max-width:500px; } .empty p { line-height:1.7; color:var(--muted); }
    .result-list { max-width:900px; } article { padding:18px 0; border-top:1px solid var(--line); } .result-source { display:flex; justify-content:space-between; font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; }
    article h2 { margin:6px 0; font-size:18px; font-weight:500; } article a { color:var(--accent-link); overflow-wrap:anywhere; text-decoration:none; } article a:hover { text-decoration:underline; } article p { line-height:1.7; margin-top:7px; overflow-wrap:anywhere; }
    .url { font-size:12px; overflow-wrap:anywhere; line-height:1.5; } .found-via { margin-top:8px; font:11px var(--font-mono); overflow-wrap:anywhere; } .more { margin-top:16px; }
    .coverage { font-size:12px; margin-bottom:18px; } .coverage-row { display:flex; flex-wrap:wrap; gap:10px; padding:6px 0; } code { overflow-wrap:anywhere; }
    .secondary > .muted { margin-top:12px; line-height:1.7; } .inline-form { display:flex; gap:12px; align-items:end; margin:24px 0; } .inline-form label { flex:1; max-width:400px; } .profile-row { display:flex; gap:8px; padding:14px 0; border-top:1px solid var(--line); } .profile-row input { flex:1; }
    .empty-small { padding:24px 0; color:var(--muted); } .history-row { display:flex; justify-content:space-between; gap:24px; padding:18px 0; text-align:left; background:none; border:0; border-bottom:1px solid var(--line); border-radius:0; width:100%; }
    .history-row span:first-child { display:flex; flex-direction:column; gap:8px; min-width:0; } .history-row strong { overflow-wrap:anywhere; font-weight:500; } time { font-size:12px; color:var(--muted); } .history-row > span:last-child { white-space:nowrap; font-variant-numeric:tabular-nums; }
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
    @media(max-width:1000px) { .workspace { grid-template-columns:270px minmax(0,1fr); } .results,.secondary { padding:22px 20px; } .heading { flex-wrap:wrap; } }
    @media(max-width:680px) { header { flex-wrap:wrap; gap:8px 12px; padding:12px; } .brand { font-size:18px; } nav { order:3; width:100%; min-height:38px; } nav button { padding:6px 8px; } .preferences { gap:4px; } .preferences select { width:90px; } .workspace { display:block; padding:0 8px 8px; } aside { padding:12px 8px 20px; } aside form { gap:12px; } textarea { min-height:110px; } main { border-radius:10px; } .results,.secondary { padding:20px 14px; } .tools { flex-wrap:wrap; } .tools input { width:100%; min-width:140px; } .profile-row { flex-wrap:wrap; } .profile-row input { flex-basis:100%; } .inline-form { align-items:stretch; flex-direction:column; } }
  `;
}
