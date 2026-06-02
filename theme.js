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

    function updateButtons(theme) {
        const label = theme === "dark" ? "Light mode" : "Dark mode";
        document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
            button.textContent = label;
            button.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
        });
    }

    function applyTheme(theme) {
        const nextTheme = theme === "dark" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", nextTheme);
        updateButtons(nextTheme);
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

    function toggleTheme() {
        const current = document.documentElement.getAttribute("data-theme") || preferredTheme();
        setTheme(current === "dark" ? "light" : "dark");
    }

    function initButtons() {
        document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
            button.addEventListener("click", toggleTheme);
        });
        applyTheme(document.documentElement.getAttribute("data-theme") || preferredTheme());
    }

    applyTheme(preferredTheme());

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initButtons);
    } else {
        initButtons();
    }

    window.synthesixTheme = {
        applyTheme,
        setTheme,
        toggleTheme,
    };
})();
