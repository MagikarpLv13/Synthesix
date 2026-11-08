import type { BrowserState, SxBrowserApp } from "./components/sx-browser-app";

type Action = Record<string, unknown> & { action: string };
declare global {
  interface Window {
    synthesixDispatch?: (payload: string) => void;
    synthesixHome: {
      setState: (patch: Partial<BrowserState>) => void;
      consumeAction: () => Action | null;
      heartbeat: () => boolean;
    };
  }
}

function installHome() {
  const app = document.querySelector<SxBrowserApp>("sx-browser-app");
  if (!app) return;
  window.name = "synthesix-home";
  const pending: Action[] = [];
  let ready = false;
  let lastContact = 0;
  window.synthesixHome = {
    setState(patch) { ready = true; lastContact = Date.now(); app.model = { ...app.model, ...patch, connected: true }; },
    consumeAction() { return pending.shift() ?? null; },
    heartbeat() { lastContact = Date.now(); return ready; },
  };
  setInterval(() => {
    if (lastContact && Date.now() - lastContact > 10000) {
      ready = false;
      app.model = { ...app.model, connected: false, running: false, status: "Application disconnected. Launch Synthesix to use this page.", isError: true };
    }
  }, 2000);
  app.addEventListener("sx-browser-action", (event: Event) => {
    const action = (event as CustomEvent<Action>).detail;
    if (typeof window.synthesixDispatch === "function") {
      window.synthesixDispatch(JSON.stringify(action));
    } else if (app.model.connected && pending.length < 32) {
      pending.push(action);
    } else {
      window.synthesixHome.setState({ status: "Application disconnected. Launch Synthesix to use this page.", isError: true });
    }
  });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", installHome, { once: true });
else installHome();
