/**
 * Design tokens for contexts that do NOT load theme.css — primarily the overlay
 * injected into third-party pages. Keep these values in sync with the light-mode
 * `:root` tokens in theme.css. App pages inherit the real tokens from theme.css,
 * so components must always reference them as `var(--token, fallback)`.
 */
export const tokensCss = `
:host {
  --accent: #2563EB;
  --accent-strong: #1D4ED8;
  --accent-soft: #DBEAFE;
  --accent-ink: #1D4ED8;
  --surface: #FFFFFF;
  --surface-2: #F1F5F9;
  --text: #0F172A;
  --muted: #64748B;
  --line: #CBD5E1;
  --success: #16A34A;
  --success-soft: #DCFCE7;
  --success-ink: #166534;
  --danger: #DC2626;
  --radius-sm: 6px;
  --radius-md: 8px;
  --shadow-soft: 0 8px 22px rgba(15, 23, 42, 0.18);
}
`;
