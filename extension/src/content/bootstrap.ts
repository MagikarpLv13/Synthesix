const extensionVersion = chrome.runtime.getManifest().version;
const OVERLAY_HOST_ID = "__synthesix-save-overlay";
const OVERLAY_SCRIPT_ID = "__synthesix-extension-overlay-script";
const OVERLAY_SCRIPT_PATH = "dist/overlay-main.js";
const OVERLAY_MAIN_SOURCE = "synthesix-overlay-main";
const OVERLAY_CONTENT_SOURCE = "synthesix-extension-content";
const OVERLAY_CONTEXT_STORAGE_KEY = "synthesixOverlayContext";
const REINSERT_THROTTLE_MS = 5000;

let lastInstallAttempt = 0;
let overlayScriptLoaded = false;
let messageCounter = 0;
let activeContext: unknown = {};

const bridgeToken = makeBridgeToken();

document.documentElement.dataset.synthesixExt = extensionVersion;

function postTargetOrigin(): string {
  return window.location.origin && window.location.origin !== "null"
    ? window.location.origin
    : "*";
}

function makeBridgeToken(): string {
  const bytes = new Uint8Array(16);
  try {
    crypto.getRandomValues(bytes);
  } catch (_error) {
    for (let index = 0; index < bytes.length; index += 1) {
      bytes[index] = Math.floor(Math.random() * 256);
    }
  }
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function isBlockedOverlayUrl(location: Location = window.location): boolean {
  const host = location.hostname.toLowerCase();
  const path = location.pathname.toLowerCase();
  if (host.includes("lens.google.") || host.includes("maps.google.")) {
    return true;
  }
  return host.includes(".google.") && (path === "/maps" || path.startsWith("/maps/"));
}

function hasOverlayHost(): boolean {
  return document.getElementById(OVERLAY_HOST_ID) !== null;
}

function postInstallRequest(): void {
  window.postMessage(
    {
      source: OVERLAY_CONTENT_SOURCE,
      token: bridgeToken,
      type: "synthesix:install-overlay",
      context: activeContext,
    },
    postTargetOrigin(),
  );
}

function postContextUpdate(context: unknown): void {
  activeContext = context && typeof context === "object" ? context : {};
  window.postMessage(
    {
      source: OVERLAY_CONTENT_SOURCE,
      token: bridgeToken,
      type: "synthesix:context-update",
      context: activeContext,
    },
    postTargetOrigin(),
  );
}

function postButtonStatus(message: unknown): void {
  window.postMessage(
    {
      source: OVERLAY_CONTENT_SOURCE,
      token: bridgeToken,
      type: "synthesix:button-status",
      status: message,
    },
    postTargetOrigin(),
  );
}

function loadStoredContext(onLoaded: () => void): void {
  chrome.storage.local.get(OVERLAY_CONTEXT_STORAGE_KEY, (items) => {
    if (chrome.runtime.lastError) {
      console.debug("[Synthesix] context storage unavailable", {
        error: chrome.runtime.lastError.message,
      });
    } else {
      activeContext = items[OVERLAY_CONTEXT_STORAGE_KEY] ?? {};
    }
    onLoaded();
  });
}

function injectOverlayScript(): void {
  if (isBlockedOverlayUrl()) {
    return;
  }
  if (hasOverlayHost()) {
    return;
  }
  const now = Date.now();
  if (now - lastInstallAttempt < REINSERT_THROTTLE_MS) {
    return;
  }
  lastInstallAttempt = now;

  if (overlayScriptLoaded) {
    postInstallRequest();
    return;
  }
  if (document.getElementById(OVERLAY_SCRIPT_ID)) {
    return;
  }

  const script = document.createElement("script");
  script.id = OVERLAY_SCRIPT_ID;
  script.src = chrome.runtime.getURL(OVERLAY_SCRIPT_PATH);
  script.async = false;
  script.dataset.synthesixToken = bridgeToken;
  script.dataset.synthesixVersion = extensionVersion;
  script.onload = () => {
    overlayScriptLoaded = true;
    script.remove();
    postInstallRequest();
  };
  script.onerror = () => {
    script.remove();
    console.warn("[Synthesix] overlay-main.js failed to load");
  };
  (document.head || document.documentElement).appendChild(script);
}

function sendRuntimeMessage(message: unknown, onResponse?: (response: unknown) => void): void {
  chrome.runtime.sendMessage(message, (response) => {
    if (chrome.runtime.lastError) {
      console.warn("[Synthesix] sendMessage failed", chrome.runtime.lastError.message);
      onResponse?.({
        ok: false,
        error: chrome.runtime.lastError.message,
      });
      return;
    }
    onResponse?.(response);
  });
}

function sendSpikeMessage(payload?: unknown): void {
  sendRuntimeMessage({
    type: "synthesix:spike",
    version: extensionVersion,
    href: window.location.href,
    sentAt: performance.now(),
    sentAtEpochMs: Date.now(),
    payload: payload ?? null,
  });
}

function relayOverlayAction(data: Record<string, unknown>): void {
  const id =
    typeof data.id === "string" && data.id
      ? data.id
      : `overlay-${Date.now()}-${messageCounter += 1}`;
  sendRuntimeMessage(
    {
      type: "synthesix:overlay-action",
      id,
      version: extensionVersion,
      href: window.location.href,
      sourceToken: typeof data.sourceToken === "string" ? data.sourceToken : bridgeToken,
      sentAt: performance.now(),
      sentAtEpochMs: Date.now(),
      action: data.action ?? null,
    },
    (response) => {
      window.postMessage(
        {
          source: OVERLAY_CONTENT_SOURCE,
          token: bridgeToken,
          type: "synthesix:overlay-ack",
          id,
          response: response ?? null,
        },
        postTargetOrigin(),
      );
    },
  );
}

window.synthesixExt = {
  dispatchSpike: sendSpikeMessage,
};

window.addEventListener("synthesix:spike-dispatch", (event) => {
  sendSpikeMessage(event instanceof CustomEvent ? event.detail : null);
});

window.addEventListener("message", (event) => {
  // Brave can expose a different WindowProxy between the page main world and
  // the content-script isolated world; authenticate with the bridge token.
  const data = event.data as Record<string, unknown> | null;
  if (
    !data
    || data.source !== OVERLAY_MAIN_SOURCE
    || data.token !== bridgeToken
    || data.type !== "synthesix:overlay-action"
  ) {
    return;
  }
  relayOverlayAction(data);
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (
    typeof message === "object"
    && message !== null
    && "type" in message
    && message.type === "synthesix:ping"
  ) {
    sendResponse({
      ok: true,
      source: "synthesix-content",
      version: extensionVersion,
    });
  }
  if (
    typeof message === "object"
    && message !== null
    && "type" in message
    && message.type === "synthesix:button-status"
  ) {
    postButtonStatus(message);
    sendResponse({ ok: true });
  }

  return false;
});

chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName !== "local" || !(OVERLAY_CONTEXT_STORAGE_KEY in changes)) {
    return;
  }
  postContextUpdate(changes[OVERLAY_CONTEXT_STORAGE_KEY].newValue ?? {});
});

loadStoredContext(() => {
  injectOverlayScript();
});

const observer = new MutationObserver(() => {
  injectOverlayScript();
});
observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

export {};
