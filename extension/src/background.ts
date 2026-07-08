type QueuedRuntimeMessage = {
  message: unknown;
  receivedAt: number;
  sender: {
    tabId?: number;
    tabUrl?: string;
    url?: string;
  };
};

type BackendContextMessage = {
  payload: unknown;
  type: "synthesix:context-update";
};

type BackendButtonStatusMessage = {
  kind: "archive" | "capture" | "save";
  message: string;
  state: string;
  tabId: number;
  type: "synthesix:button-status";
};

type BackendMessage = BackendButtonStatusMessage | BackendContextMessage;

const OVERLAY_CONTEXT_STORAGE_KEY = "synthesixOverlayContext";
const MAX_QUEUED_MESSAGES = 100;
const queuedMessages: QueuedRuntimeMessage[] = [];

function canDispatchToBackend(): boolean {
  return typeof globalThis.synthesixDispatch === "function";
}

function dispatchToBackend(payload: QueuedRuntimeMessage): boolean {
  if (!canDispatchToBackend()) {
    return false;
  }

  const message = payload.message;
  const action =
    typeof message === "object"
    && message !== null
    && "type" in message
    && message.type === "synthesix:overlay-action"
      ? "extension_overlay_action"
      : "extension_spike_message";
  globalThis.synthesixDispatch(
    JSON.stringify({
      v: 1,
      action,
      tabId: payload.sender.tabId,
      url: payload.sender.tabUrl ?? payload.sender.url,
      payload,
    }),
  );
  return true;
}

function queueMessage(message: unknown, sender: SynthesixChromeMessageSender): number {
  const payload = {
    message,
    receivedAt: Date.now(),
    sender: {
      tabId: sender.tab?.id,
      tabUrl: sender.tab?.url,
      url: sender.url,
    },
  };
  queuedMessages.push(payload);

  if (queuedMessages.length > MAX_QUEUED_MESSAGES) {
    queuedMessages.shift();
  }

  dispatchToBackend(payload);
  return queuedMessages.length;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function normalizeBackendMessage(message: unknown): BackendMessage | null {
  if (!isRecord(message) || typeof message.type !== "string") {
    return null;
  }
  if (message.type === "synthesix:context-update") {
    return {
      type: "synthesix:context-update",
      payload: message.payload ?? {},
    };
  }
  if (
    message.type === "synthesix:button-status"
    && typeof message.tabId === "number"
    && ["archive", "capture", "save"].includes(String(message.kind))
  ) {
    return {
      type: "synthesix:button-status",
      tabId: message.tabId,
      kind: message.kind as BackendButtonStatusMessage["kind"],
      state: String(message.state || ""),
      message: String(message.message || ""),
    };
  }
  return null;
}

function storageSet(items: Record<string, unknown>): Promise<void> {
  return new Promise((resolve, reject) => {
    chrome.storage.local.set(items, () => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message || "storage set failed"));
        return;
      }
      resolve();
    });
  });
}

function sendTabMessage(tabId: number, message: unknown): Promise<boolean> {
  return new Promise((resolve) => {
    chrome.tabs.sendMessage(tabId, message, () => {
      if (chrome.runtime.lastError) {
        console.debug("[Synthesix] tab message skipped", {
          tabId,
          error: chrome.runtime.lastError.message,
        });
        resolve(false);
        return;
      }
      resolve(true);
    });
  });
}

async function receiveBackendMessage(rawMessage: unknown): Promise<boolean> {
  const message = normalizeBackendMessage(rawMessage);
  if (!message) {
    console.debug("[Synthesix] invalid backend message", rawMessage);
    return false;
  }
  if (message.type === "synthesix:context-update") {
    await storageSet({
      [OVERLAY_CONTEXT_STORAGE_KEY]: message.payload,
    });
    return true;
  }
  return sendTabMessage(message.tabId, message);
}

chrome.runtime.onInstalled.addListener((details) => {
  console.info("[Synthesix] extension installed", {
    reason: details.reason,
    version: chrome.runtime.getManifest().version,
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const queued = queueMessage(message, sender);
  const backendBinding = canDispatchToBackend();
  console.debug("[Synthesix] message queued", {
    queued,
    backendBinding,
    tabId: sender.tab?.id,
    url: sender.url ?? sender.tab?.url,
  });
  sendResponse({ ok: true, queued, backendBinding });
  return false;
});

globalThis.synthesixReceiveBackendMessage = receiveBackendMessage;

export {};
