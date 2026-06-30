import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

/**
 * <sx-saved-page-card
 *    class="investigation-result" data-result-id="…" …filter data-attrs…
 *    observations="3" first-seen="…" last-seen="…" initial="T" site="tiktok.com">
 *   <a slot="title" class="result-title" href="…" title="full title — url">…</a>
 *   <label slot="star" class="favorite-toggle">…favorite checkbox (JS-bound)…</label>
 *   <label slot="status" class="status-control">…status select (JS-bound)…</label>
 *   <a slot="menu" class="saved-card__menu-item" href="…wayback…">…</a>
 *   <button slot="menu" class="saved-card__menu-item start-page-monitor">…</button>
 *   <button slot="menu" class="saved-card__menu-item saved-card__menu-item--danger remove-saved-page">…</button>
 *   <div slot="tags" data-result-tags-display>…</div>
 *   <textarea data-result-notes hidden></textarea><input type="hidden" data-result-tags>
 * </sx-saved-page-card>
 *
 * Compact, grid-friendly saved-page card. Two tight rows: (1) a brand-coloured
 * platform favicon + title + favorite + overflow menu, (2) status + observation
 * pills. The favicon shows the platform glyph (TikTok, Instagram, X, …) when the
 * domain is recognised, otherwise a coloured letter avatar. The full URL lives in
 * the title tooltip; the description is shown in the workspace rail on click.
 * The Lit element owns the chrome and the "⋯" overflow menu; everything that
 * carries translatable words or is wired by the generated-page inline JS stays in
 * light-DOM slots, so i18n and the existing CDP dispatch keep working untouched.
 */

interface Brand {
  /** Glyph colour, or "currentColor" for monochrome marks (adapts to theme). */
  color: string;
  /** Simple Icons (CC0) 24×24 single-path glyph. */
  path: string;
}

/** Platform glyphs keyed by registrable label. Extend by adding entries here. */
const BRANDS: Record<string, Brand> = {
  tiktok: {
    color: "#EE1D52",
    path: "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z",
  },
  instagram: {
    color: "#E4405F",
    path: "M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077",
  },
  x: {
    color: "currentColor",
    path: "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z",
  },
  facebook: {
    color: "#1877F2",
    path: "M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z",
  },
  youtube: {
    color: "#FF0000",
    path: "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z",
  },
  googlemaps: {
    color: "#1A73E8",
    path: "M19.527 4.799c1.212 2.608.937 5.678-.405 8.173-1.101 2.047-2.744 3.74-4.098 5.614-.619.858-1.244 1.75-1.669 2.727-.141.325-.263.658-.383.992-.121.333-.224.673-.34 1.008-.109.314-.236.684-.627.687h-.007c-.466-.001-.579-.53-.695-.887-.284-.874-.581-1.713-1.019-2.525-.51-.944-1.145-1.817-1.79-2.671L19.527 4.799zM8.545 7.705l-3.959 4.707c.724 1.54 1.821 2.863 2.871 4.18.247.31.494.622.737.936l4.984-5.925-.029.01c-1.741.601-3.691-.291-4.392-1.987a3.377 3.377 0 0 1-.209-.716c-.063-.437-.077-.761-.004-1.198l.001-.007zM5.492 3.149l-.003.004c-1.947 2.466-2.281 5.88-1.117 8.77l4.785-5.689-.058-.05-3.607-3.035zM14.661.436l-3.838 4.563a.295.295 0 0 1 .027-.01c1.6-.551 3.403.15 4.22 1.626.176.319.323.683.377 1.045.068.446.085.773.012 1.22l-.003.016 3.836-4.561A8.382 8.382 0 0 0 14.67.439l-.009-.003zM9.466 5.868L14.162.285l-.047-.012A8.31 8.31 0 0 0 11.986 0a8.439 8.439 0 0 0-6.169 2.766l-.016.018 3.665 3.084z",
  },
  telegram: {
    color: "#229ED9",
    path: "M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z",
  },
  snapchat: {
    color: "#E0A800",
    path: "M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.09.401.09.3-.016.659-.12 1.033-.301.165-.088.344-.104.464-.104.182 0 .359.029.509.09.45.149.734.479.734.838.015.449-.39.839-1.213 1.168-.089.029-.209.075-.344.119-.45.135-1.139.36-1.333.81-.09.224-.061.524.12.868l.015.015c.06.136 1.526 3.475 4.791 4.014.255.044.435.27.42.509 0 .075-.015.149-.045.225-.24.569-1.273.988-3.146 1.271-.059.091-.12.375-.164.57-.029.179-.074.36-.134.553-.076.271-.27.405-.555.405h-.03c-.135 0-.313-.031-.538-.074-.36-.075-.765-.135-1.273-.135-.3 0-.599.015-.913.074-.6.104-1.123.464-1.723.884-.853.599-1.826 1.288-3.294 1.288-.06 0-.119-.015-.18-.015h-.149c-1.468 0-2.427-.675-3.279-1.288-.599-.42-1.107-.779-1.707-.884-.314-.045-.629-.074-.928-.074-.54 0-.958.089-1.272.149-.211.043-.391.074-.54.074-.374 0-.523-.224-.583-.42-.061-.192-.09-.389-.135-.567-.046-.181-.105-.494-.166-.57-1.918-.222-2.95-.642-3.189-1.226-.031-.063-.052-.15-.055-.225-.015-.243.165-.465.42-.509 3.264-.54 4.73-3.879 4.791-4.02l.016-.029c.18-.345.224-.645.119-.869-.195-.434-.884-.658-1.332-.809-.121-.029-.24-.074-.346-.119-1.107-.435-1.257-.93-1.197-1.273.09-.479.674-.793 1.168-.793.146 0 .27.029.383.074.42.194.789.3 1.104.3.234 0 .384-.06.465-.105l-.046-.569c-.098-1.626-.225-3.651.307-4.837C7.392 1.077 10.739.807 11.727.807l.419-.015h.06z",
  },
  pinterest: {
    color: "#BD081C",
    path: "M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z",
  },
  reddit: {
    color: "#FF4500",
    path: "M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z",
  },
  whatsapp: {
    color: "#25D366",
    path: "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z",
  },
};

/** Fallback letter-avatar palette, keyed by site for at-a-glance scanning. */
const FAVICON_COLORS = [
  "#38bdf8",
  "#a78bfa",
  "#34d399",
  "#fbbf24",
  "#f472b6",
  "#22d3ee",
  "#c084fc",
  "#fb7185",
];

@customElement("sx-saved-page-card")
export class SxSavedPageCard extends LitElement {
  /** Total observation count, shown as the eye pill. */
  @property({ type: Number })
  observations = 0;

  /** ISO timestamp of the first observation (clock pill + tooltip). */
  @property({ attribute: "first-seen" })
  firstSeen = "";

  /** ISO timestamp of the latest observation. */
  @property({ attribute: "last-seen" })
  lastSeen = "";

  /** One-letter avatar fallback when the domain has no known brand glyph. */
  @property()
  initial = "";

  /** Host string (netloc), used to pick the brand glyph and fallback colour. */
  @property()
  site = "";

  /** Imported local document → show a document glyph instead of a brand/letter. */
  @property({ type: Boolean })
  imported = false;

  @state()
  private _menuOpen = false;

  static styles = css`
    :host {
      display: block;
      position: relative;
      min-width: 0;
      border: 1px solid var(--line, #1e293b);
      border-radius: 10px;
      background: var(--surface, #0b1220);
      cursor: pointer;
      transition: border-color 120ms ease;
    }
    :host(:hover),
    :host(.is-inspected) {
      border-color: var(--accent, #6366f1);
    }
    :host(.is-inspected) {
      box-shadow: 0 0 0 1px var(--accent, #6366f1);
    }
    :host([hidden]) {
      display: none;
    }
    /* Raise the whole card above its grid neighbours while the overflow menu is
       open, so the popover is not clipped behind the next card. */
    :host([menu-open]) {
      z-index: 20;
    }
    .card {
      display: grid;
      gap: 7px;
      padding: 11px 12px;
    }
    .head {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .favicon {
      flex: 0 0 auto;
      display: grid;
      place-items: center;
      width: 24px;
      height: 24px;
      border-radius: 7px;
      font: 700 12px/1 var(--font-ui, system-ui, sans-serif);
      text-transform: uppercase;
    }
    .favicon svg {
      width: 15px;
      height: 15px;
    }
    ::slotted([slot="title"]) {
      flex: 0 1 auto;
      min-width: 0;
    }
    ::slotted([slot="star"]) {
      flex: 0 0 auto;
      margin-left: auto;
    }
    .menu-wrap {
      position: relative;
      display: inline-flex;
      flex: 0 0 auto;
    }
    .kebab {
      display: grid;
      place-items: center;
      width: 30px;
      height: 30px;
      padding: 0;
      border: 0;
      border-radius: 7px;
      background: transparent;
      color: var(--muted, #94a3b8);
      cursor: pointer;
      transition: background-color 120ms ease, color 120ms ease;
    }
    .kebab:hover,
    .kebab[aria-expanded="true"] {
      background: color-mix(in srgb, var(--accent, #6366f1) 16%, transparent);
      color: var(--text, #e2e8f0);
    }
    .kebab:focus-visible {
      outline: 2px solid var(--accent, #6366f1);
      outline-offset: 1px;
    }
    .kebab svg {
      width: 18px;
      height: 18px;
    }
    .menu {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      z-index: 30;
      min-width: 212px;
      padding: 5px;
      border: 1px solid var(--line, #334155);
      border-radius: 10px;
      background: var(--surface, #0b1220);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.38);
    }
    .menu[hidden] {
      display: none;
    }
    .menu__label {
      padding: 4px 8px 6px;
      color: var(--muted, #94a3b8);
      font-size: 11px;
    }
    .sub {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }
    ::slotted([slot="status"]) {
      flex: 0 0 auto;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      flex: 0 0 auto;
      color: var(--muted, #94a3b8);
      font-size: 11px;
      font-variant-numeric: tabular-nums;
    }
    .pill svg {
      width: 13px;
      height: 13px;
      opacity: 0.85;
    }
    ::slotted([slot="tags"]) {
      min-width: 0;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.addEventListener("keydown", this._onKeyDown);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.removeEventListener("keydown", this._onKeyDown);
    document.removeEventListener("pointerdown", this._onDocPointerDown, true);
  }

  private _toggleMenu = (event: Event): void => {
    // Keep the whole-card click handler (opens the inspector) from firing.
    event.stopPropagation();
    this._menuOpen ? this._closeMenu() : this._openMenu();
  };

  private _openMenu(): void {
    this._menuOpen = true;
    this.toggleAttribute("menu-open", true);
    document.addEventListener("pointerdown", this._onDocPointerDown, true);
  }

  private _closeMenu(): void {
    if (!this._menuOpen) return;
    this._menuOpen = false;
    this.toggleAttribute("menu-open", false);
    document.removeEventListener("pointerdown", this._onDocPointerDown, true);
  }

  private _onDocPointerDown = (event: Event): void => {
    if (!event.composedPath().includes(this)) this._closeMenu();
  };

  private _onKeyDown = (event: KeyboardEvent): void => {
    if (event.key === "Escape" && this._menuOpen) {
      event.stopPropagation();
      this._closeMenu();
    }
  };

  /** Close after a menu action runs, but let the action itself proceed. */
  private _onMenuClick = (): void => {
    this._closeMenu();
  };

  /** Resolve the platform glyph for this card's site, or null for unknown. */
  private _brand(): Brand | null {
    const site = this.site.trim().toLowerCase();
    if (!site) return null;
    const specials: Record<string, string> = {
      "t.me": "telegram",
      "telegram.org": "telegram",
      "wa.me": "whatsapp",
      "youtu.be": "youtube",
      "fb.com": "facebook",
      "x.com": "x",
      "twitter.com": "x",
    };
    let key = specials[site];
    if (!key) {
      const parts = site.split(".").filter(Boolean);
      const label = parts.length >= 2 ? parts[parts.length - 2] : parts[0] ?? "";
      const alias: Record<string, string> = { twitter: "x", google: "googlemaps" };
      key = alias[label] ?? label;
    }
    return BRANDS[key] ?? null;
  }

  private get _faviconColor(): string {
    const key = (this.site || this.initial || "").toLowerCase();
    if (!key) return "var(--accent, #6366f1)";
    let hash = 0;
    for (let i = 0; i < key.length; i += 1) {
      hash = (hash * 31 + key.charCodeAt(i)) | 0;
    }
    return FAVICON_COLORS[Math.abs(hash) % FAVICON_COLORS.length];
  }

  private _fmt(iso: string, opts: Intl.DateTimeFormatOptions): string {
    if (!iso) return "";
    const date = new Date(iso.replace(/(\.\d{3})\d+/, "$1"));
    if (Number.isNaN(date.getTime())) return "";
    return new Intl.DateTimeFormat(undefined, opts).format(date);
  }

  private _renderFavicon() {
    const siteTitle = this.imported ? "Document importé" : this.site;
    const docGlyph = html`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 3v4a1 1 0 0 0 1 1h4"></path>
      <path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2Z"></path>
    </svg>`;
    if (this.imported) {
      const color = this._faviconColor;
      const style = `background: color-mix(in srgb, ${color} 18%, transparent); color: ${color};`;
      return html`<span class="favicon" style=${style} title=${siteTitle} aria-hidden="true">${docGlyph}</span>`;
    }
    const brand = this._brand();
    if (brand) {
      const isText = brand.color === "currentColor";
      const glyphColor = isText ? "var(--text, #e2e8f0)" : brand.color;
      const tint = isText ? "var(--muted, #94a3b8)" : brand.color;
      const style = `background: color-mix(in srgb, ${tint} 18%, transparent); color: ${glyphColor};`;
      return html`<span class="favicon" style=${style} title=${siteTitle} aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d=${brand.path}></path></svg>
      </span>`;
    }
    const color = this._faviconColor;
    const style = `background: color-mix(in srgb, ${color} 18%, transparent); color: ${color};`;
    return html`<span class="favicon" style=${style} title=${siteTitle} aria-hidden="true">${this.initial || "·"}</span>`;
  }

  private _renderSeenPill() {
    const shortOpts: Intl.DateTimeFormatOptions = { day: "numeric", month: "short" };
    const fullOpts: Intl.DateTimeFormatOptions = {
      dateStyle: "medium",
      timeStyle: "short",
    };
    const first = this._fmt(this.firstSeen, shortOpts);
    const last = this._fmt(this.lastSeen, shortOpts);
    if (!first && !last) return null;
    const text = first && last && first !== last ? `${first} → ${last}` : last || first;
    const firstFull = this._fmt(this.firstSeen, fullOpts);
    const lastFull = this._fmt(this.lastSeen, fullOpts);
    const title = [
      firstFull ? `Première observation : ${firstFull}` : "",
      lastFull ? `Dernière observation : ${lastFull}` : "",
    ]
      .filter(Boolean)
      .join(" · ");
    return html`<span class="pill" title=${title} aria-label=${title}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9"></circle>
        <path d="M12 7v5l3 2"></path>
      </svg>
      ${text}
    </span>`;
  }

  render() {
    const obsCount = Number(this.observations) || 0;
    const obsLabel = `${obsCount} observation${obsCount === 1 ? "" : "s"}`;
    return html`
      <article class="card" part="card">
        <div class="head">
          ${this._renderFavicon()}
          <slot name="title"></slot>
          <slot name="star"></slot>
          <div class="menu-wrap">
            <button
              type="button"
              class="kebab"
              title="Actions supplémentaires"
              aria-label="Actions supplémentaires"
              aria-haspopup="menu"
              aria-expanded=${this._menuOpen ? "true" : "false"}
              @click=${this._toggleMenu}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <circle cx="12" cy="5" r="1.7"></circle>
                <circle cx="12" cy="12" r="1.7"></circle>
                <circle cx="12" cy="19" r="1.7"></circle>
              </svg>
            </button>
            <div class="menu" role="menu" ?hidden=${!this._menuOpen} @click=${this._onMenuClick}>
              <div class="menu__label">Actions supplémentaires</div>
              <slot name="menu"></slot>
            </div>
          </div>
        </div>
        <div class="sub">
          <slot name="status"></slot>
          <span class="pill" title=${obsLabel} aria-label=${obsLabel}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            ${obsCount}
          </span>
          ${this._renderSeenPill()}
        </div>
        <slot name="tags"></slot>
        <slot></slot>
      </article>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-saved-page-card": SxSavedPageCard;
  }
}
