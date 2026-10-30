/**
 * Design tokens for contexts that do NOT load theme.css — primarily the overlay
 * injected into third-party pages. Keep these values in sync with the light-mode
 * `:root` tokens in theme.css. App pages inherit the real tokens from theme.css,
 * so components must always reference them as `var(--token, fallback)`.
 */
export const tokensCss = `
:host {
  --accent: #2A46A6;
  --accent-strong: #23408F;
  --accent-soft: #E4E8F6;
  --accent-ink: #17225A;
  --accent-on-dark: #8AA0EE;
  --surface: #FBF9F4;
  --surface-2: #FCFBF8;
  --surface-sunken: #ECE8DE;
  --text: #191A1E;
  --text-muted: #56513F;
  --muted: #56513F;
  --line: #DAD4C7;
  --ink-surface: #17181D;
  --ink-surface-2: #1F2027;
  --ink-border: #2B2D34;
  --on-ink: #EDEAE2;
  --on-ink-strong: #F7F5EF;
  --success: #28613C;
  --success-soft: #E1EEE3;
  --success-ink: #1E4B2E;
  --danger: #B33A3A;
  --font-ui: "Public Sans", system-ui, Arial, sans-serif;
  --font-mono: "IBM Plex Mono", Consolas, monospace;
  --radius-sm: 7px;
  --radius-md: 8px;
  --shadow-soft: 0 10px 26px rgba(23, 24, 30, 0.22);
}
`;
