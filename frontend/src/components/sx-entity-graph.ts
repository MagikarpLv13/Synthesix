import { LitElement, html, css, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";

/**
 * <sx-entity-graph>
 *   <script type="application/json" data-graph-data>
 *     {"nodes":[{"id":"e1","label":"…","category":"Personne","props":3,"sources":2}],
 *      "edges":[{"source":"e1","target":"e2","label":"PDG de"}]}
 *   </script>
 * </sx-entity-graph>
 *
 * Relationship graph for investigation entities. Nodes = graph entities (colored
 * by category), edges = entity↔entity relations. Force-directed layout, drawn as
 * SVG and updated imperatively for smoothness (Lit only owns the host shell, the
 * SVG skeleton, the toolbar and the empty state).
 *
 * Interaction:
 *  - wheel = zoom to cursor, drag background = pan, drag node = reposition,
 *  - click node = dispatch `sx-entity-select` ({ detail: { id } }),
 *  - hover/focus node = highlight its neighborhood.
 *
 * Data may be provided via the `data` property or a child JSON `<script>`.
 */

export interface GraphNode {
  id: string;
  label: string;
  category?: string;
  props?: number;
  sources?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  label?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface Particle {
  node: GraphNode;
  x: number;
  y: number;
  vx: number;
  vy: number;
  r: number;
  degree: number;
  fixed: boolean;
  el: SVGGElement;
  circle: SVGCircleElement;
}

interface Link {
  edge: GraphEdge;
  a: Particle;
  b: Particle;
  line: SVGLineElement;
  label: SVGTextElement | null;
}

const SVG_NS = "http://www.w3.org/2000/svg";

/** Deterministic, dark/light-friendly palette keyed by category. */
const CATEGORY_COLORS: Record<string, string> = {
  personne: "#38bdf8",
  entreprise: "#a78bfa",
  organisation: "#a78bfa",
  lieu: "#34d399",
  adresse: "#34d399",
  "événement": "#fbbf24",
  evenement: "#fbbf24",
  document: "#f472b6",
  identifiant: "#f59e0b",
};
const FALLBACK_PALETTE = [
  "#38bdf8",
  "#a78bfa",
  "#34d399",
  "#fbbf24",
  "#f472b6",
  "#22d3ee",
  "#c084fc",
];

function colorFor(category: string | undefined): string {
  const key = (category ?? "").trim().toLowerCase();
  if (key && CATEGORY_COLORS[key]) return CATEGORY_COLORS[key];
  if (!key) return "#94a3b8";
  let hash = 0;
  for (let i = 0; i < key.length; i += 1) {
    hash = (hash * 31 + key.charCodeAt(i)) | 0;
  }
  return FALLBACK_PALETTE[Math.abs(hash) % FALLBACK_PALETTE.length];
}

@customElement("sx-entity-graph")
export class SxEntityGraph extends LitElement {
  /** Graph payload. Falls back to a child JSON `<script data-graph-data>`. */
  @property({ attribute: false })
  data: GraphData | null = null;

  @state()
  private _empty = false;

  static styles = css`
    :host {
      display: block;
      position: relative;
      width: 100%;
      height: var(--graph-height, 560px);
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 10px);
      background: var(--surface, #0b1220);
      overflow: hidden;
      contain: strict;
    }
    .stage {
      display: block;
      width: 100%;
      height: 100%;
      cursor: grab;
      touch-action: none;
      user-select: none;
    }
    .stage.is-panning {
      cursor: grabbing;
    }
    .edge {
      stroke: var(--line, #334155);
      stroke-width: 1.4px;
      transition: stroke 0.18s ease, stroke-opacity 0.18s ease;
    }
    .edge-label {
      fill: var(--muted, #94a3b8);
      font-size: 10px;
      paint-order: stroke;
      stroke: var(--surface, #0b1220);
      stroke-width: 3px;
      stroke-linejoin: round;
      pointer-events: none;
      opacity: 0.92;
      transition: opacity 0.18s ease;
    }
    .node {
      cursor: pointer;
    }
    .node circle {
      stroke: var(--surface, #0b1220);
      stroke-width: 2px;
      transition: filter 0.18s ease;
    }
    .node text {
      fill: var(--text, #e2e8f0);
      font-size: 11px;
      font-weight: 600;
      paint-order: stroke;
      stroke: var(--surface, #0b1220);
      stroke-width: 3.5px;
      stroke-linejoin: round;
      pointer-events: none;
    }
    .node:focus-visible {
      outline: none;
    }
    .node:focus-visible circle {
      stroke: var(--accent, #6366f1);
      stroke-width: 3px;
    }
    /* Highlight state driven imperatively. */
    .stage.is-hovering .edge {
      stroke-opacity: 0.15;
    }
    .stage.is-hovering .node {
      opacity: 0.25;
    }
    .stage.is-hovering .edge.is-active {
      stroke-opacity: 1;
      stroke: var(--accent, #6366f1);
    }
    .stage.is-hovering .edge-label {
      opacity: 0.1;
    }
    .stage.is-hovering .edge-label.is-active {
      opacity: 1;
    }
    .stage.is-hovering .node.is-active {
      opacity: 1;
    }
    .node circle:hover {
      filter: brightness(1.15);
    }
    .toolbar {
      position: absolute;
      top: 10px;
      right: 10px;
      display: inline-flex;
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line, #334155);
      border-radius: 8px;
      background: color-mix(in srgb, var(--surface, #0b1220) 86%, transparent);
      backdrop-filter: blur(4px);
    }
    .toolbar button {
      display: inline-grid;
      place-items: center;
      width: 28px;
      height: 28px;
      padding: 0;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--muted, #94a3b8);
      font: inherit;
      font-size: 15px;
      line-height: 1;
      cursor: pointer;
    }
    .toolbar button:hover {
      background: color-mix(in srgb, var(--accent, #6366f1) 18%, transparent);
      color: var(--text, #e2e8f0);
    }
    .toolbar button:focus-visible {
      outline: 2px solid var(--accent, #6366f1);
      outline-offset: 1px;
    }
    .legend {
      position: absolute;
      left: 10px;
      bottom: 10px;
      display: flex;
      flex-wrap: wrap;
      gap: 4px 12px;
      max-width: calc(100% - 20px);
      padding: 6px 10px;
      border: 1px solid var(--line, #334155);
      border-radius: 8px;
      background: color-mix(in srgb, var(--surface, #0b1220) 86%, transparent);
      backdrop-filter: blur(4px);
      font-size: 11px;
      color: var(--muted, #94a3b8);
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .legend i {
      width: 9px;
      height: 9px;
      border-radius: 50%;
    }
    .empty {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      padding: 24px;
      text-align: center;
      color: var(--muted, #94a3b8);
      font-size: 13px;
    }
    .hint {
      position: absolute;
      bottom: 10px;
      right: 10px;
      color: var(--muted, #94a3b8);
      font-size: 10px;
      opacity: 0.7;
      pointer-events: none;
    }
  `;

  private _particles: Particle[] = [];
  private _links: Link[] = [];
  private _byId = new Map<string, Particle>();
  private _legend: Array<{ label: string; color: string }> = [];

  // Viewport transform (world → screen): screen = world * k + t.
  private _k = 1;
  private _tx = 0;
  private _ty = 0;

  private _width = 0;
  private _height = 0;
  private _resizeObs: ResizeObserver | null = null;
  private _laidOut = false;

  // Pointer state.
  private _mode: "idle" | "pan" | "node" = "idle";
  private _dragParticle: Particle | null = null;
  private _startX = 0;
  private _startY = 0;
  private _moved = false;
  private _activeId: string | null = null;

  private get _svg(): SVGSVGElement | null {
    return this.renderRoot.querySelector<SVGSVGElement>(".stage");
  }
  private get _viewport(): SVGGElement | null {
    return this.renderRoot.querySelector<SVGGElement>(".viewport");
  }
  private get _edgesG(): SVGGElement | null {
    return this.renderRoot.querySelector<SVGGElement>(".edges");
  }
  private get _nodesG(): SVGGElement | null {
    return this.renderRoot.querySelector<SVGGElement>(".nodes");
  }

  connectedCallback(): void {
    super.connectedCallback();
    if (!this.data) {
      this.data = this._readInlineData();
    }
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this._resizeObs?.disconnect();
    this._resizeObs = null;
  }

  firstUpdated(): void {
    const svg = this._svg;
    if (svg) {
      svg.addEventListener("wheel", this._onWheel, { passive: false });
      svg.addEventListener("pointerdown", this._onPointerDown);
    }
    this._resizeObs = new ResizeObserver((entries) => {
      const box = entries[0]?.contentRect;
      if (!box) return;
      this._width = box.width;
      this._height = box.height;
      if (!this._laidOut && this._width > 0 && this._height > 0) {
        this._build();
      }
    });
    this._resizeObs.observe(this);
  }

  updated(changed: PropertyValues): void {
    if (changed.has("data")) {
      this._laidOut = false;
      if (this._width > 0 && this._height > 0) {
        this._build();
      }
    }
  }

  private _readInlineData(): GraphData | null {
    const script = this.querySelector<HTMLScriptElement>(
      "script[data-graph-data]",
    );
    if (!script?.textContent) return null;
    try {
      const parsed = JSON.parse(script.textContent) as GraphData;
      if (Array.isArray(parsed.nodes)) return parsed;
    } catch {
      /* ignore malformed payload */
    }
    return null;
  }

  // ---- Build & layout -----------------------------------------------------

  private _build(): void {
    const edgesG = this._edgesG;
    const nodesG = this._nodesG;
    if (!edgesG || !nodesG) return;

    // The inline <script> child may not have been parsed yet when
    // connectedCallback fired (the element upgrades on its opening tag), so
    // resolve the payload here — _build runs after the DOM is fully parsed.
    if (!this.data) {
      this.data = this._readInlineData();
    }

    edgesG.replaceChildren();
    nodesG.replaceChildren();
    this._particles = [];
    this._links = [];
    this._byId.clear();

    const nodes = this.data?.nodes ?? [];
    const edges = this.data?.edges ?? [];
    this._empty = nodes.length === 0;
    if (this._empty) {
      this._laidOut = true;
      return;
    }

    // Degree (for node radius), seeded from valid edges only.
    const degree = new Map<string, number>();
    const valid: GraphEdge[] = [];
    const ids = new Set(nodes.map((n) => n.id));
    for (const e of edges) {
      if (e.source === e.target) continue;
      if (!ids.has(e.source) || !ids.has(e.target)) continue;
      valid.push(e);
      degree.set(e.source, (degree.get(e.source) ?? 0) + 1);
      degree.set(e.target, (degree.get(e.target) ?? 0) + 1);
    }

    // Seed positions at random inside a disk: an asymmetric start lets the
    // force layout relax into an organic shape instead of staying ring-like.
    const n = nodes.length;
    const spread = 50 * Math.sqrt(n) + 60;
    const categories = new Map<string, string>();
    nodes.forEach((node, i) => {
      void i;
      const deg = degree.get(node.id) ?? 0;
      const color = colorFor(node.category);
      if (node.category) categories.set(node.category, color);
      const seedAngle = Math.random() * Math.PI * 2;
      const seedRadius = Math.sqrt(Math.random()) * spread;
      const particle: Particle = {
        node,
        x: Math.cos(seedAngle) * seedRadius,
        y: Math.sin(seedAngle) * seedRadius,
        vx: 0,
        vy: 0,
        r: 8 + Math.min(14, deg * 2.2),
        degree: deg,
        fixed: false,
        el: this._makeNode(node, color, deg),
        circle: null as unknown as SVGCircleElement,
      };
      particle.circle = particle.el.querySelector("circle") as SVGCircleElement;
      this._particles.push(particle);
      this._byId.set(node.id, particle);
      nodesG.appendChild(particle.el);
    });

    for (const e of valid) {
      const a = this._byId.get(e.source);
      const b = this._byId.get(e.target);
      if (!a || !b) continue;
      const line = document.createElementNS(SVG_NS, "line");
      line.setAttribute("class", "edge");
      line.setAttribute("marker-end", "url(#sx-graph-arrow)");
      edgesG.appendChild(line);
      let label: SVGTextElement | null = null;
      if (e.label) {
        label = document.createElementNS(SVG_NS, "text");
        label.setAttribute("class", "edge-label");
        label.setAttribute("text-anchor", "middle");
        label.textContent = e.label;
        edgesG.appendChild(label);
      }
      this._links.push({ edge: e, a, b, line, label });
    }

    this._legend = [...categories.entries()].map(([label, color]) => ({
      label,
      color,
    }));

    this._laidOut = true;
    // Compute the whole layout synchronously, then freeze it: the graph never
    // drifts on its own — nodes only move when the user drags them.
    this._settle();
    this.fit();
    this.requestUpdate();
  }

  private _makeNode(node: GraphNode, color: string, deg: number): SVGGElement {
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "node");
    g.setAttribute("tabindex", "0");
    g.setAttribute("role", "button");
    g.setAttribute(
      "aria-label",
      `${node.label}${node.category ? ` (${node.category})` : ""}`,
    );
    g.dataset.id = node.id;

    const circle = document.createElementNS(SVG_NS, "circle");
    const r = 8 + Math.min(14, deg * 2.2);
    circle.setAttribute("r", String(r));
    circle.setAttribute("fill", color);
    g.appendChild(circle);

    const text = document.createElementNS(SVG_NS, "text");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dy", String(-r - 6));
    const label = node.label.length > 28 ? `${node.label.slice(0, 27)}…` : node.label;
    text.textContent = label;
    g.appendChild(text);

    g.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" || ev.key === " ") {
        ev.preventDefault();
        this._select(node.id);
      }
    });
    g.addEventListener("pointerenter", () => this._highlight(node.id));
    g.addEventListener("pointerleave", () => this._highlight(null));
    g.addEventListener("focus", () => this._highlight(node.id));
    g.addEventListener("blur", () => this._highlight(null));
    return g;
  }

  // ---- Force simulation ---------------------------------------------------

  private _step(alpha: number): void {
    const particles = this._particles;
    const n = particles.length;
    const repulsion = 7000;
    const center = 0.012;

    for (let i = 0; i < n; i += 1) {
      const p = particles[i];
      for (let j = i + 1; j < n; j += 1) {
        const q = particles[j];
        let dx = p.x - q.x;
        let dy = p.y - q.y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 0.01) {
          dx = Math.random() - 0.5;
          dy = Math.random() - 0.5;
          d2 = dx * dx + dy * dy;
        }
        const d = Math.sqrt(d2);
        const force = Math.min(repulsion / d2, 90);
        const fx = (dx / d) * force;
        const fy = (dy / d) * force;
        p.vx += fx;
        p.vy += fy;
        q.vx -= fx;
        q.vy -= fy;
      }
      // Gravity toward origin keeps the graph compact and on screen.
      p.vx -= p.x * center;
      p.vy -= p.y * center;
    }

    // Spring attraction along links.
    for (const link of this._links) {
      const { a, b } = link;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const target = 150 + a.r + b.r;
      const k = (d - target) * 0.06;
      const fx = (dx / d) * k;
      const fy = (dy / d) * k;
      a.vx += fx;
      a.vy += fy;
      b.vx -= fx;
      b.vy -= fy;
    }

    const damping = 0.85;
    for (const p of particles) {
      if (p.fixed) {
        p.vx = 0;
        p.vy = 0;
        continue;
      }
      p.vx *= damping;
      p.vy *= damping;
      p.x += p.vx * alpha;
      p.y += p.vy * alpha;
    }
  }

  /** Run the simulation to completion in one synchronous pass, then stop. */
  private _settle(): void {
    let alpha = 1;
    for (let i = 0; i < 450 && alpha > 0.004; i += 1) {
      this._step(alpha);
      alpha *= 0.985;
    }
    this._draw();
  }

  private _draw(): void {
    const vp = this._viewport;
    if (vp) {
      vp.setAttribute(
        "transform",
        `translate(${this._tx} ${this._ty}) scale(${this._k})`,
      );
    }
    for (const p of this._particles) {
      p.el.setAttribute("transform", `translate(${p.x} ${p.y})`);
    }
    for (const link of this._links) {
      const { a, b, line, label } = link;
      // Stop the line at the node edge so the arrowhead is visible.
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const ux = dx / d;
      const uy = dy / d;
      line.setAttribute("x1", String(a.x + ux * a.r));
      line.setAttribute("y1", String(a.y + uy * a.r));
      line.setAttribute("x2", String(b.x - ux * (b.r + 6)));
      line.setAttribute("y2", String(b.y - uy * (b.r + 6)));
      if (label) {
        label.setAttribute("x", String((a.x + b.x) / 2));
        label.setAttribute("y", String((a.y + b.y) / 2));
      }
    }
  }

  // ---- View transform helpers ---------------------------------------------

  fit(): void {
    if (this._particles.length === 0 || this._width === 0) return;
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    for (const p of this._particles) {
      minX = Math.min(minX, p.x - p.r);
      minY = Math.min(minY, p.y - p.r);
      maxX = Math.max(maxX, p.x + p.r);
      maxY = Math.max(maxY, p.y + p.r);
    }
    const pad = 48;
    const w = maxX - minX || 1;
    const h = maxY - minY || 1;
    const k = Math.min(
      (this._width - pad * 2) / w,
      (this._height - pad * 2) / h,
      1.6,
    );
    this._k = Math.max(0.1, k);
    this._tx = this._width / 2 - ((minX + maxX) / 2) * this._k;
    this._ty = this._height / 2 - ((minY + maxY) / 2) * this._k;
    this._draw();
  }

  private _zoomBy(factor: number, cx?: number, cy?: number): void {
    const px = cx ?? this._width / 2;
    const py = cy ?? this._height / 2;
    const k = Math.max(0.1, Math.min(4, this._k * factor));
    // Keep the point under the cursor stable.
    this._tx = px - ((px - this._tx) * k) / this._k;
    this._ty = py - ((py - this._ty) * k) / this._k;
    this._k = k;
    this._draw();
  }

  private _toWorld(clientX: number, clientY: number): { x: number; y: number } {
    const rect = this.getBoundingClientRect();
    const sx = clientX - rect.left;
    const sy = clientY - rect.top;
    return { x: (sx - this._tx) / this._k, y: (sy - this._ty) / this._k };
  }

  // ---- Interaction --------------------------------------------------------

  private _onWheel = (ev: WheelEvent): void => {
    ev.preventDefault();
    const rect = this.getBoundingClientRect();
    const factor = ev.deltaY < 0 ? 1.12 : 1 / 1.12;
    this._zoomBy(factor, ev.clientX - rect.left, ev.clientY - rect.top);
  };

  private _onPointerDown = (ev: PointerEvent): void => {
    if (ev.button !== 0) return;
    const target = ev.target as Element;
    const nodeEl = target.closest(".node") as SVGGElement | null;
    this._startX = ev.clientX;
    this._startY = ev.clientY;
    this._moved = false;
    this._svg?.setPointerCapture(ev.pointerId);

    if (nodeEl?.dataset.id) {
      const particle = this._byId.get(nodeEl.dataset.id);
      if (particle) {
        this._mode = "node";
        this._dragParticle = particle;
        particle.fixed = true;
      }
    } else {
      this._mode = "pan";
      this._svg?.classList.add("is-panning");
    }
    window.addEventListener("pointermove", this._onPointerMove);
    window.addEventListener("pointerup", this._onPointerUp);
  };

  private _onPointerMove = (ev: PointerEvent): void => {
    const dx = ev.clientX - this._startX;
    const dy = ev.clientY - this._startY;
    if (!this._moved && Math.hypot(dx, dy) > 4) this._moved = true;

    if (this._mode === "pan") {
      this._tx += ev.movementX;
      this._ty += ev.movementY;
      this._draw();
    } else if (this._mode === "node" && this._dragParticle) {
      const world = this._toWorld(ev.clientX, ev.clientY);
      this._dragParticle.x = world.x;
      this._dragParticle.y = world.y;
      // Move only the dragged node — the rest of the graph stays put.
      this._draw();
    }
  };

  private _onPointerUp = (ev: PointerEvent): void => {
    window.removeEventListener("pointermove", this._onPointerMove);
    window.removeEventListener("pointerup", this._onPointerUp);
    this._svg?.classList.remove("is-panning");

    if (this._mode === "node" && this._dragParticle) {
      const particle = this._dragParticle;
      particle.fixed = false;
      // A click without movement opens the entity; a drag just leaves the node
      // where it was dropped (no re-simulation, so nothing else shifts).
      if (!this._moved) this._select(particle.node.id);
    }
    this._mode = "idle";
    this._dragParticle = null;
    void ev;
  };

  private _select(id: string): void {
    this.dispatchEvent(
      new CustomEvent("sx-entity-select", {
        detail: { id },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private _highlight(id: string | null): void {
    if (id === this._activeId) return;
    this._activeId = id;
    const svg = this._svg;
    if (!svg) return;

    if (!id) {
      svg.classList.remove("is-hovering");
      for (const p of this._particles) p.el.classList.remove("is-active");
      for (const l of this._links) {
        l.line.classList.remove("is-active");
        l.label?.classList.remove("is-active");
      }
      return;
    }

    const neighbors = new Set<string>([id]);
    for (const l of this._links) {
      const touches = l.a.node.id === id || l.b.node.id === id;
      l.line.classList.toggle("is-active", touches);
      l.label?.classList.toggle("is-active", touches);
      if (touches) {
        neighbors.add(l.a.node.id);
        neighbors.add(l.b.node.id);
      }
    }
    for (const p of this._particles) {
      p.el.classList.toggle("is-active", neighbors.has(p.node.id));
    }
    svg.classList.add("is-hovering");
  }

  render() {
    return html`
      <svg class="stage" role="img" aria-label="Graphe de relations des entités">
        <defs>
          <marker
            id="sx-graph-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--line, #334155)"></path>
          </marker>
        </defs>
        <g class="viewport">
          <g class="edges"></g>
          <g class="nodes"></g>
        </g>
      </svg>
      ${this._empty
        ? html`<div class="empty">
            Aucune relation à afficher. Créez des entités et liez-les depuis le
            rail pour voir apparaître le graphe.
          </div>`
        : html`
            <div class="toolbar">
              <button type="button" title="Zoom avant" aria-label="Zoom avant" @click=${() => this._zoomBy(1.2)}>+</button>
              <button type="button" title="Zoom arrière" aria-label="Zoom arrière" @click=${() => this._zoomBy(1 / 1.2)}>−</button>
              <button type="button" title="Ajuster" aria-label="Ajuster la vue" @click=${() => this.fit()}>⤢</button>
            </div>
            ${this._legend.length
              ? html`<div class="legend">
                  ${this._legend.map(
                    (item) =>
                      html`<span><i style=${`background:${item.color}`}></i>${item.label}</span>`,
                  )}
                </div>`
              : null}
          `}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-entity-graph": SxEntityGraph;
  }
}
