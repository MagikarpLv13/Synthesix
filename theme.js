(function () {
    const storageKey = "synthesix-theme";

    function preferredTheme() {
        try {
            const stored = window.localStorage.getItem(storageKey);
            if (stored === "dark" || stored === "light") {
                return stored;
            }
        } catch (_error) {
            // Ignore storage failures and fall back to the OS preference.
        }

        if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
            return "dark";
        }
        return "light";
    }

    function applyTheme(theme) {
        const nextTheme = theme === "dark" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", nextTheme);
    }

    function setTheme(theme) {
        const nextTheme = theme === "dark" ? "dark" : "light";
        try {
            window.localStorage.setItem(storageKey, nextTheme);
        } catch (_error) {
            // The theme still applies even if it cannot be persisted.
        }
        applyTheme(nextTheme);
    }

    applyTheme(preferredTheme());

    window.synthesixTheme = {
        applyTheme,
        setTheme,
    };
})();
