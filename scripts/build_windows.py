"""Build the Windows app from the committed UI bundle, without runtime data."""

from pathlib import Path
import shutil
import sys


def main() -> None:
    if sys.platform != "win32":
        raise SystemExit("Build this Windows executable on Windows.")
    from PyInstaller.__main__ import run

    root = Path(__file__).resolve().parents[1]
    for output in [root / "dist", root / "build"]:
        if not output.resolve().is_relative_to(root) or output.resolve() == root:
            raise SystemExit("Build output must stay inside the project directory.")
    resources = ["index.html", "theme.css", "theme.js", "i18n.js", "assets"]
    args = [
        "--noconfirm", "--onedir", "--windowed", "--name", "Synthesix",
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build" / "pyinstaller"),
        "--specpath", str(root / "build"),
        "--paths", str(root),
        "--collect-submodules", "zendriver",
        "--copy-metadata", "zendriver",
    ]
    for resource in resources:
        args.extend(["--add-data", f"{root / resource}:{resource if resource == 'assets' else '.'}"])
    run([*args, str(root / "main.py")])
    (root / "dist" / "Synthesix" / "LISEZ-MOI.txt").write_text(
        "Synthesix\n\nOuvrir Synthesix.exe. Chrome ou Brave doit être installé.\n"
        "Conserver le répertoire _internal à côté de l'exécutable.\n"
        "Les données sont conservées dans %LOCALAPPDATA%/Synthesix.\n",
        encoding="utf-8",
    )
    shutil.make_archive(str(root / "dist" / "Synthesix-Windows"), "zip", root / "dist", "Synthesix")


if __name__ == "__main__":
    main()
