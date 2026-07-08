declare global {
  interface SynthesixChromeManifest {
    version: string;
  }

  interface SynthesixChromeTab {
    id?: number;
    url?: string;
  }

  interface SynthesixChromeMessageSender {
    id?: string;
    tab?: SynthesixChromeTab;
    url?: string;
  }

  interface SynthesixChromeInstalledDetails {
    id?: string;
    previousVersion?: string;
    reason: string;
  }

  type SynthesixChromeSendResponse = (response?: unknown) => void;

  interface SynthesixChromeRuntime {
    lastError?: {
      message?: string;
    };
    getManifest(): SynthesixChromeManifest;
    getURL(path: string): string;
    sendMessage(
      message: unknown,
      responseCallback?: (response: unknown) => void,
    ): void;
    onInstalled: {
      addListener(listener: (details: SynthesixChromeInstalledDetails) => void): void;
    };
    onMessage: {
      addListener(
        listener: (
          message: unknown,
          sender: SynthesixChromeMessageSender,
          sendResponse: SynthesixChromeSendResponse,
        ) => boolean | void,
      ): void;
    };
  }

  interface SynthesixChromeStorageChange {
    oldValue?: unknown;
    newValue?: unknown;
  }

  interface SynthesixChromeStorageArea {
    get(
      keys: string | string[] | Record<string, unknown> | null,
      callback: (items: Record<string, unknown>) => void,
    ): void;
    set(items: Record<string, unknown>, callback?: () => void): void;
  }

  interface SynthesixChromeStorage {
    local: SynthesixChromeStorageArea;
    onChanged: {
      addListener(
        listener: (
          changes: Record<string, SynthesixChromeStorageChange>,
          areaName: string,
        ) => void,
      ): void;
    };
  }

  interface SynthesixChromeTabs {
    query(
      queryInfo: Record<string, unknown>,
      callback: (tabs: SynthesixChromeTab[]) => void,
    ): void;
    sendMessage(
      tabId: number,
      message: unknown,
      responseCallback?: (response: unknown) => void,
    ): void;
  }

  interface SynthesixChromeApi {
    runtime: SynthesixChromeRuntime;
    storage: SynthesixChromeStorage;
    tabs: SynthesixChromeTabs;
  }

  const chrome: SynthesixChromeApi;

  interface Window {
    synthesixExt?: {
      dispatchSpike(payload?: unknown): void;
    };
    __synthesixFocusGuardInstalled?: boolean;
  }

  function synthesixDispatch(payload: string): void;
  function synthesixReceiveBackendMessage(message: unknown): Promise<boolean>;
}

export {};
