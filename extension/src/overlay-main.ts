import "../../frontend/src/overlay/index";
import type { SxOverlayRoot } from "../../frontend/src/overlay/sx-overlay-root";

type OverlayActionName =
  | "archive_page_to_investigation"
  | "attach_selection_to_graph_entity"
  | "capture_evidence_to_investigation"
  | "create_graph_entity_from_selection"
  | "focus_home"
  | "observe_saved_page"
  | "save_page_to_investigation";

type OverlayActionPayload = {
  action: OverlayActionName;
  [key: string]: unknown;
};

type GraphEntity = {
  id: string;
  label: string;
  tags?: string[];
  propertyKeys?: string[];
};

type OverlayContext = {
  baseTagsets?: string[];
  id?: string;
  title?: string;
  existingTags?: string[];
  graphEntities?: GraphEntity[];
  tagsetProperties?: Record<string, string[]>;
  tagsetPropertyTypes?: Record<string, Record<string, string>>;
};

type PagePayload = {
  browserContext: {
    devicePixelRatio: number;
    language: string;
    userAgent: string;
    viewportHeight: number;
    viewportWidth: number;
  };
  description: string;
  referrer: string;
  title: string;
  url: string;
};

type OverlayActionElement = HTMLElement & {
  ariaText?: string;
  disabled?: boolean;
  icon?: string;
  iconOnly?: boolean;
  label?: string;
  state?: string;
  titleText?: string;
  variant?: string;
};

type CaptureAttach = {
  entityId: string;
  propertyKey: string;
  propertyType: string;
};

type CaptureMenuElement = HTMLElement & {
  ensureCaptureName?: (value: string) => void;
  graphEntities?: GraphEntity[];
  open?: boolean;
  reset?: () => void;
  tagsetProperties?: Record<string, string[]>;
};

type EntityMenuElement = HTMLElement & {
  baseTagsets?: string[];
  existingTags?: string[];
  graphEntities?: GraphEntity[];
  tagsetProperties?: Record<string, string[]>;
  tagsetPropertyTypes?: Record<string, Record<string, string>>;
};

type SelectionBoxElement = HTMLElement;

type SynthesixOverlayHost = SxOverlayRoot & {
  __synthesixArchiveButton?: OverlayActionElement;
  __synthesixCaptureButton?: OverlayActionElement;
  __synthesixDefaultCaptureName?: () => string;
  __synthesixPagePayload?: () => PagePayload;
  __synthesixQueueCapture?: (
    scope: "viewport" | "region",
    selection: Record<string, number>,
    captureName: string,
    attach: CaptureAttach | null,
  ) => void;
  __synthesixSaveButton?: OverlayActionElement;
  __synthesixSetArchiveState?: (state: string, tooltip?: string) => void;
  __synthesixSetButtonState?: (state: string, text: string) => void;
  __synthesixSetCaptureState?: (state: string, tooltip?: string) => void;
  __synthesixSetEntityTagsets?: (tags: string[]) => void;
  __synthesixSetGraphEntities?: (entities: GraphEntity[]) => void;
  __synthesixSetTagsetMetadata?: (context: OverlayContext) => void;
  __synthesixStartRegionSelection?: (
    captureName: string,
    attach: CaptureAttach | null,
  ) => void;
};

type PendingAction = {
  action: OverlayActionName;
};

const OVERLAY_HOST_ID = "__synthesix-save-overlay";
const SELECTION_ID = "__synthesix-evidence-selection";
const COLLAPSED_STORAGE_KEY = "synthesix:external-overlay-collapsed";
const MAIN_SOURCE = "synthesix-overlay-main";
const CONTENT_SOURCE = "synthesix-extension-content";
const currentScript = document.currentScript as HTMLScriptElement | null;
const bridgeToken = currentScript?.dataset.synthesixToken || "";
const extensionVersion = currentScript?.dataset.synthesixVersion || "0.1.0";
const pendingActions = new Map<string, PendingAction>();
let messageCounter = 0;
let activeContext: OverlayContext = {};

function postTargetOrigin(): string {
  return window.location.origin && window.location.origin !== "null"
    ? window.location.origin
    : "*";
}

if (bridgeToken) {
  document.documentElement.dataset.synthesixOverlayToken = bridgeToken;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function stringValue(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.map(String).filter((item) => item.trim())
    : [];
}

function stringArrayMap(value: unknown): Record<string, string[]> {
  if (!isRecord(value)) {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).map(([key, entries]) => [key, stringArray(entries)]),
  );
}

function nestedStringMap(value: unknown): Record<string, Record<string, string>> {
  if (!isRecord(value)) {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).map(([tag, properties]) => [
      tag,
      isRecord(properties)
        ? Object.fromEntries(
            Object.entries(properties).map(([key, type]) => [key, String(type || "")]),
          )
        : {},
    ]),
  );
}

function normalizeContext(rawContext: unknown): OverlayContext {
  if (!isRecord(rawContext)) {
    return {};
  }
  return {
    baseTagsets: stringArray(rawContext.baseTagsets),
    id: stringValue(rawContext.id),
    title: stringValue(rawContext.title),
    existingTags: stringArray(rawContext.existingTags),
    graphEntities: Array.isArray(rawContext.graphEntities)
      ? rawContext.graphEntities
          .filter(isRecord)
          .map((entity) => ({
            id: stringValue(entity.id),
            label: stringValue(entity.label),
            tags: stringArray(entity.tags),
            propertyKeys: stringArray(entity.propertyKeys),
          }))
          .filter((entity) => entity.id.trim())
      : [],
    tagsetProperties: stringArrayMap(rawContext.tagsetProperties),
    tagsetPropertyTypes: nestedStringMap(rawContext.tagsetPropertyTypes),
  };
}

function pagePayload(): PagePayload {
  const metaDescription = document.querySelector<HTMLMetaElement>(
    'meta[name="description" i]',
  );
  return {
    url: window.location.href,
    title: document.title || window.location.hostname,
    description: metaDescription?.content || "",
    referrer: document.referrer || "",
    browserContext: {
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio || 1,
      language: navigator.language || "",
      userAgent: navigator.userAgent || "",
    },
  };
}

function queueAction(action: OverlayActionPayload): string {
  const id = `overlay-${Date.now()}-${messageCounter += 1}`;
  pendingActions.set(id, { action: action.action });
  window.postMessage(
    {
      source: MAIN_SOURCE,
      token: bridgeToken,
      type: "synthesix:overlay-action",
      id,
      sourceToken: bridgeToken,
      action,
    },
    postTargetOrigin(),
  );
  return id;
}

function applyActionAttributes(
  element: OverlayActionElement,
  values: {
    ariaText?: string;
    icon?: string;
    iconOnly?: boolean;
    label?: string;
    titleText?: string;
    variant?: string;
  },
): void {
  if (values.variant) {
    element.variant = values.variant;
    element.setAttribute("variant", values.variant);
  }
  if (values.icon) {
    element.icon = values.icon;
    element.setAttribute("icon", values.icon);
  }
  if (values.iconOnly) {
    element.iconOnly = true;
    element.setAttribute("icon-only", "");
  }
  if (values.label) {
    element.label = values.label;
    element.setAttribute("label", values.label);
    element.textContent = values.label;
  }
  if (values.ariaText) {
    element.ariaText = values.ariaText;
    element.setAttribute("aria-text", values.ariaText);
  }
  if (values.titleText) {
    element.titleText = values.titleText;
    element.setAttribute("title-text", values.titleText);
  }
}

function createActionButton(
  markerAttribute: string,
  values: Parameters<typeof applyActionAttributes>[1],
): OverlayActionElement {
  const button = document.createElement("sx-overlay-action") as OverlayActionElement;
  button.setAttribute(markerAttribute, "");
  button.setAttribute("slot", "toolbar");
  applyActionAttributes(button, values);
  return button;
}

function defaultCaptureName(): string {
  const now = new Date();
  const pad = (value: number): string => String(value).padStart(2, "0");
  return (
    `screenshot_${now.getFullYear()}-`
    + `${pad(now.getMonth() + 1)}-`
    + `${pad(now.getDate())}_`
    + `${pad(now.getHours())}-`
    + `${pad(now.getMinutes())}-`
    + `${pad(now.getSeconds())}`
  );
}

function restoreCollapsed(host: SynthesixOverlayHost): void {
  try {
    host.collapsed = window.localStorage.getItem(COLLAPSED_STORAGE_KEY) === "1";
    host.toggleAttribute("collapsed", host.collapsed);
  } catch (_error) {
    host.collapsed = false;
  }
}

function setButtonTitle(button: OverlayActionElement, title: string): void {
  button.title = title;
  button.titleText = title;
  button.setAttribute("title-text", title);
}

function installOverlay(rawContext: unknown = activeContext): SynthesixOverlayHost | null {
  activeContext = normalizeContext(rawContext);
  const existing = document.getElementById(OVERLAY_HOST_ID);
  if (existing && !existing.hasAttribute("data-synthesix-extension-overlay")) {
    return null;
  }

  let host = existing as SynthesixOverlayHost | null;
  if (!host) {
    host = document.createElement("sx-overlay-root") as SynthesixOverlayHost;
    host.id = OVERLAY_HOST_ID;
    host.setAttribute("data-synthesix-overlay-root", "");
    host.setAttribute("data-synthesix-extension-overlay", extensionVersion);
    restoreCollapsed(host);

    const saveButton = createActionButton("data-synthesix-save-page", {
      ariaText: "Save page to active Synthesix investigation",
      icon: "mark",
      label: "Save page",
      variant: "primary",
    });
    host.__synthesixSaveButton = saveButton;
    host.__synthesixPagePayload = pagePayload;
    host.__synthesixSetButtonState = (state, text) => {
      host?.setSaveButtonState(state, text);
    };
    saveButton.addEventListener("click", () => {
      if (!host?.dataset.investigationId) {
        queueAction({ action: "focus_home" });
        return;
      }
      if (saveButton.dataset.state === "saved") {
        return;
      }
      host.__synthesixSetButtonState?.("saving", "Saving...");
      queueAction({
        action: "save_page_to_investigation",
        investigationId: host.dataset.investigationId,
        page: host.__synthesixPagePayload?.(),
      });
    });

    const archiveButton = createActionButton("data-synthesix-archive", {
      icon: "archive",
      iconOnly: true,
      variant: "archive",
    });
    host.__synthesixArchiveButton = archiveButton;
    host.__synthesixSetArchiveState = (
      state,
      tooltip = "Save page with HTML archive",
    ) => {
      host?.setArchiveState(state, tooltip);
    };
    archiveButton.addEventListener("click", () => {
      if (!host?.dataset.investigationId) {
        queueAction({ action: "focus_home" });
        return;
      }
      host.__synthesixSetArchiveState?.("archiving", "Saving HTML archive...");
      queueAction({
        action: "archive_page_to_investigation",
        investigationId: host.dataset.investigationId,
        page: host.__synthesixPagePayload?.(),
      });
    });

    const captureButton = createActionButton("data-synthesix-capture", {
      icon: "camera",
      iconOnly: true,
      variant: "capture",
    });
    host.__synthesixCaptureButton = captureButton;

    const captureMenu = document.createElement(
      "sx-overlay-capture-menu",
    ) as CaptureMenuElement;
    captureMenu.setAttribute("data-synthesix-capture-menu", "");
    captureMenu.tagsetProperties = {};
    host.__synthesixDefaultCaptureName = defaultCaptureName;
    host.__synthesixSetCaptureState = (
      state,
      tooltip = "Capture screenshot",
    ) => {
      host?.setCaptureState(state, tooltip);
    };
    host.__synthesixQueueCapture = (
      scope,
      selection,
      captureName,
      attach,
    ) => {
      host?.__synthesixSetCaptureState?.("capturing", "Capturing evidence...");
      if (host) {
        host.style.display = "none";
      }
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          queueAction({
            action: "capture_evidence_to_investigation",
            investigationId: host?.dataset.investigationId,
            captureScope: scope,
            captureName: String(captureName || "").trim(),
            selection,
            attach: attach || null,
            page: host?.__synthesixPagePayload?.(),
          });
          captureMenu.reset?.();
        });
      });
    };
    host.__synthesixStartRegionSelection = (captureName, attach) => {
      if (!host) {
        return;
      }
      const overlayHost = host;
      overlayHost.style.display = "none";
      document.getElementById(SELECTION_ID)?.remove();
      const selectionBox = document.createElement(
        "sx-overlay-selection-box",
      ) as SelectionBoxElement;
      selectionBox.id = SELECTION_ID;
      selectionBox.addEventListener("synthesix-region-selected", (event) => {
        selectionBox.remove();
        const region = (event as CustomEvent<Record<string, number>>).detail || {};
        host?.__synthesixQueueCapture?.(
          "region",
          {
            x: region.x,
            y: region.y,
            width: region.width,
            height: region.height,
          },
          captureName,
          attach,
        );
      });
      selectionBox.addEventListener("synthesix-region-cancel", () => {
        selectionBox.remove();
        overlayHost.style.display = "block";
      });
      (document.documentElement || document.body).appendChild(selectionBox);
    };
    captureMenu.addEventListener("synthesix-capture-choice", (event) => {
      const detail = (event as CustomEvent<{
        attach?: CaptureAttach | null;
        captureName?: string;
        scope?: string;
      }>).detail || {};
      if (!host?.dataset.investigationId) {
        queueAction({ action: "focus_home" });
        return;
      }
      if (detail.scope === "viewport") {
        host.__synthesixQueueCapture?.(
          "viewport",
          {
            x: window.scrollX,
            y: window.scrollY,
            width: window.innerWidth,
            height: window.innerHeight,
          },
          detail.captureName || "",
          detail.attach || null,
        );
      } else if (detail.scope === "region") {
        host.__synthesixStartRegionSelection?.(
          detail.captureName || "",
          detail.attach || null,
        );
      }
    });
    captureButton.addEventListener("click", () => {
      if (!host?.dataset.investigationId) {
        queueAction({ action: "focus_home" });
        return;
      }
      const nextOpen = !captureMenu.hasAttribute("open");
      captureMenu.open = nextOpen;
      captureMenu.toggleAttribute("open", nextOpen);
      if (nextOpen) {
        captureMenu.ensureCaptureName?.(
          host.__synthesixDefaultCaptureName?.() || defaultCaptureName(),
        );
      }
    });

    const entityMenu = document.createElement(
      "sx-overlay-entity-menu",
    ) as EntityMenuElement;
    entityMenu.baseTagsets = [];
    entityMenu.tagsetProperties = {};
    entityMenu.tagsetPropertyTypes = {};
    host.__synthesixSetTagsetMetadata = (context) => {
      entityMenu.baseTagsets = context.baseTagsets || [];
      entityMenu.tagsetProperties = context.tagsetProperties || {};
      entityMenu.tagsetPropertyTypes = context.tagsetPropertyTypes || {};
      captureMenu.tagsetProperties = context.tagsetProperties || {};
    };
    host.__synthesixSetEntityTagsets = (tags) => {
      entityMenu.existingTags = Array.isArray(tags) ? tags : [];
    };
    host.__synthesixSetGraphEntities = (graphEntities) => {
      const entities = Array.isArray(graphEntities) ? graphEntities : [];
      entityMenu.graphEntities = entities;
      captureMenu.graphEntities = entities;
    };
    entityMenu.addEventListener("synthesix-entity-create", (event) => {
      const detail = (event as CustomEvent<Record<string, unknown>>).detail || {};
      if (!host?.dataset.investigationId) {
        queueAction({ action: "focus_home" });
        return;
      }
      queueAction({
        action: "create_graph_entity_from_selection",
        investigationId: host.dataset.investigationId,
        entity: {
          label: detail.label,
          category: detail.category,
        },
        page: host.__synthesixPagePayload?.(),
      });
    });
    entityMenu.addEventListener("synthesix-entity-attach", (event) => {
      const detail = (event as CustomEvent<Record<string, unknown>>).detail || {};
      if (!host?.dataset.investigationId) {
        queueAction({ action: "focus_home" });
        return;
      }
      queueAction({
        action: "attach_selection_to_graph_entity",
        investigationId: host.dataset.investigationId,
        entityId: detail.entityId,
        property: {
          key: detail.propertyKey,
          value: detail.label,
          property_type: detail.propertyType || "",
        },
        page: host.__synthesixPagePayload?.(),
      });
    });

    host.addEventListener("synthesix-overlay-toggle", (event) => {
      const collapsed = Boolean(
        (event as CustomEvent<{ collapsed?: boolean }>).detail?.collapsed,
      );
      try {
        window.localStorage.setItem(COLLAPSED_STORAGE_KEY, collapsed ? "1" : "0");
      } catch (_error) {}
      if (collapsed) {
        captureMenu.reset?.();
        captureMenu.open = false;
        captureMenu.removeAttribute("open");
      }
    });

    host.append(saveButton, archiveButton, captureButton, captureMenu, entityMenu);
    (document.documentElement || document.body).appendChild(host);
  }

  updateOverlayContext(host, activeContext);
  return host;
}

function updateOverlayContext(
  host: SynthesixOverlayHost,
  context: OverlayContext,
): void {
  const contextId = context.id || "";
  const contextTitle = context.title || "";
  const pageKey = `${contextId}|${window.location.href}`;
  const contextChanged = host.dataset.pageKey !== pageKey;
  host.dataset.investigationId = contextId;
  host.dataset.pageKey = pageKey;
  host.__synthesixSetTagsetMetadata?.(context);
  host.__synthesixSetGraphEntities?.(context.graphEntities || []);
  host.__synthesixSetEntityTagsets?.(context.existingTags || []);

  const button =
    host.__synthesixSaveButton
    || (host.querySelector("[data-synthesix-save-page]") as OverlayActionElement | null);
  if (!button) {
    return;
  }

  const statusUntil = Number(host.dataset.statusUntil || 0);
  const captureStatusUntil = Number(host.dataset.captureStatusUntil || 0);
  const archiveStatusUntil = Number(host.dataset.archiveStatusUntil || 0);
  if (contextChanged) {
    host.dataset.saved = "0";
    host.dataset.statusUntil = "0";
    if (contextId) {
      setButtonTitle(button, `Save this page to "${contextTitle}"`);
      host.__synthesixSetButtonState?.("idle", "Save page");
    } else {
      setButtonTitle(
        button,
        "Open Synthesix to select an investigation before saving this page",
      );
      host.__synthesixSetButtonState?.("idle", "Select investigation");
    }
    host.__synthesixSetCaptureState?.("idle", "Capture screenshot");
    host.__synthesixSetArchiveState?.("idle", "Save page with HTML archive");
  } else if (button.dataset.state === "error" && Date.now() >= statusUntil) {
    setButtonTitle(
      button,
      contextId
        ? `Save this page to "${contextTitle}"`
        : "Open Synthesix to select an investigation before saving this page",
    );
    host.__synthesixSetButtonState?.("idle", "Save page");
  }

  const captureButton =
    host.__synthesixCaptureButton
    || (host.querySelector("[data-synthesix-capture]") as OverlayActionElement | null);
  if (
    ["captured", "error"].includes(captureButton?.dataset.state || "")
    && Date.now() >= captureStatusUntil
  ) {
    host.__synthesixSetCaptureState?.("idle", "Capture screenshot");
  }

  const archiveButton =
    host.__synthesixArchiveButton
    || (host.querySelector("[data-synthesix-archive]") as OverlayActionElement | null);
  if (
    ["archived", "error"].includes(archiveButton?.dataset.state || "")
    && Date.now() >= archiveStatusUntil
  ) {
    host.__synthesixSetArchiveState?.("idle", "Save page with HTML archive");
  }

  if (contextId && host.dataset.observationKey !== pageKey) {
    host.dataset.observationKey = pageKey;
    queueAction({
      action: "observe_saved_page",
      investigationId: contextId,
      page: {
        url: window.location.href,
      },
    });
  }
}

function applyButtonStatus(rawStatus: unknown): void {
  if (!isRecord(rawStatus)) {
    return;
  }
  const host = document.getElementById(OVERLAY_HOST_ID) as SynthesixOverlayHost | null;
  if (!host) {
    return;
  }
  const kind = String(rawStatus.kind || "");
  const state = String(rawStatus.state || "");
  const message = String(rawStatus.message || "");
  const isError = state === "error";
  if (kind === "save") {
    const button =
      host.__synthesixSaveButton
      || (host.querySelector("[data-synthesix-save-page]") as OverlayActionElement | null);
    host.dataset.saved = isError ? "0" : "1";
    if (button) {
      setButtonTitle(button, message);
    }
    host.__synthesixSetButtonState?.(isError ? "error" : "saved", message);
    host.dataset.statusUntil = isError ? String(Date.now() + 1800) : "0";
  } else if (kind === "capture") {
    host.style.display = "block";
    host.__synthesixSetCaptureState?.(
      isError ? "error" : "captured",
      message,
    );
    host.dataset.captureStatusUntil = String(Date.now() + 2200);
  } else if (kind === "archive") {
    host.__synthesixSetArchiveState?.(
      isError ? "error" : "archived",
      message,
    );
    host.dataset.archiveStatusUntil = String(Date.now() + 2200);
  }
}

function applyLocalAck(id: string, response: unknown): void {
  const pending = pendingActions.get(id);
  if (!pending) {
    return;
  }
  pendingActions.delete(id);

  const host = document.getElementById(OVERLAY_HOST_ID) as SynthesixOverlayHost | null;
  if (!host) {
    return;
  }
  const record = isRecord(response) ? response : {};
  const ok = record.ok !== false;
  const backendBinding = record.backendBinding === true;
  if (backendBinding) {
    return;
  }

  if (!ok) {
    if (pending.action === "capture_evidence_to_investigation") {
      host.style.display = "block";
      host.__synthesixSetCaptureState?.("error", "Capture could not be queued");
      host.dataset.captureStatusUntil = String(Date.now() + 2200);
    } else if (pending.action === "archive_page_to_investigation") {
      host.__synthesixSetArchiveState?.("error", "Archive could not be queued");
      host.dataset.archiveStatusUntil = String(Date.now() + 2200);
    } else if (pending.action === "save_page_to_investigation") {
      host.__synthesixSetButtonState?.("error", "Save could not be queued");
      host.dataset.statusUntil = String(Date.now() + 1800);
    }
    return;
  }

  if (pending.action === "capture_evidence_to_investigation") {
    host.style.display = "block";
    host.__synthesixSetCaptureState?.("captured", "Capture queued in extension");
    host.dataset.captureStatusUntil = String(Date.now() + 2200);
  } else if (pending.action === "archive_page_to_investigation") {
    host.__synthesixSetArchiveState?.("archived", "Archive queued in extension");
    host.dataset.archiveStatusUntil = String(Date.now() + 2200);
  } else if (pending.action === "save_page_to_investigation") {
    const button = host.__synthesixSaveButton;
    host.dataset.saved = "1";
    if (button) {
      setButtonTitle(button, "Save queued in extension");
    }
    host.__synthesixSetButtonState?.("saved", "Queued");
  }
}

window.addEventListener("message", (event) => {
  // Brave can expose a different WindowProxy between extension worlds; the
  // bridge token and source label are the routing checks.
  const data = event.data;
  if (
    !isRecord(data)
    || data.source !== CONTENT_SOURCE
    || data.token !== bridgeToken
  ) {
    return;
  }

  if (data.type === "synthesix:install-overlay") {
    installOverlay(data.context);
  } else if (data.type === "synthesix:context-update") {
    installOverlay(data.context);
  } else if (data.type === "synthesix:button-status") {
    applyButtonStatus(data.status);
  } else if (
    data.type === "synthesix:overlay-ack"
    && typeof data.id === "string"
  ) {
    applyLocalAck(data.id, data.response);
  }
});

window.SynthesixExtensionOverlay = {
  install: installOverlay,
  version: extensionVersion,
};

installOverlay({});

declare global {
  interface Window {
    SynthesixExtensionOverlay?: {
      install(context?: unknown): SynthesixOverlayHost | null;
      version: string;
    };
  }
}

export {};
