if (!window.__synthesixFocusGuardInstalled) {
  window.__synthesixFocusGuardInstalled = true;

  const isOverlayNode = (node: unknown): boolean => {
    let current: unknown = node;
    while (current) {
      const element = current as HTMLElement;
      const tag = element.tagName;
      if (typeof tag === "string" && tag.startsWith("SX-OVERLAY-")) {
        return true;
      }
      const root = element.getRootNode?.();
      current =
        root && "host" in root
          ? (root as ShadowRoot).host
          : element.parentNode;
    }
    return false;
  };

  try {
    const nativeFocus = HTMLElement.prototype.focus;
    HTMLElement.prototype.focus = function synthesixGuardedFocus(
      ...args: Parameters<typeof nativeFocus>
    ): void {
      if (isOverlayNode(document.activeElement) && !isOverlayNode(this)) {
        return;
      }
      return nativeFocus.apply(this, args);
    };
  } catch (_error) {}

  const isOverlayFieldEvent = (event: Event): boolean => {
    const path = event.composedPath ? event.composedPath() : [];
    const target = path[0] as HTMLElement | undefined;
    const tag = target?.tagName;
    if (tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") {
      return false;
    }
    return path.some((node) => {
      const nodeTag = (node as HTMLElement | undefined)?.tagName;
      return typeof nodeTag === "string" && nodeTag.startsWith("SX-OVERLAY-");
    });
  };

  for (const type of ["keydown", "keypress", "keyup"]) {
    window.addEventListener(
      type,
      (event) => {
        if (isOverlayFieldEvent(event)) {
          event.stopImmediatePropagation();
          event.stopPropagation();
        }
      },
      true,
    );
  }
}

export {};
