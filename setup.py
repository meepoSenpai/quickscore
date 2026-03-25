from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from setuptools import find_packages

import tomllib as toml


def _load_pyproject(path: Path) -> Dict[str, Any]:
    with path.open("rb") as fh:
        return toml.load(fh)


def _first_maintainer(maintainers: tuple[str, str] | None):
    if not maintainers:
        return None, None
    first = maintainers[0] or {}
    return first.get("name"), first.get("email")


def _read_readme(project_section: Dict[str, Any], base: Path) -> (Optional[str], Optional[str]):
    readme = project_section.get("readme")
    if not readme:
        return None, None
    # readme can be a file name (string) or a table; handle the common string case
    if isinstance(readme, str):
        readme_path = base / readme
        if readme_path.exists():
            return readme_path.read_text(encoding="utf-8"), "text/markdown"
        return None, None
    # If it's a table, it may contain 'file' and 'content-type'
    if isinstance(readme, dict):
        file = readme.get("file")
        content_type = readme.get("content-type")
        if file:
            readme_path = base / file
            if readme_path.exists():
                return readme_path.read_text(encoding="utf-8"), content_type or "text/markdown"
    return None, None


def _normalize_dependencies(deps: Optional[List[Any]]) -> List[str]:
    if not deps:
        return []
    normalized: List[str] = []
    for d in deps:
        # dependency entries are typically strings like "package>=1.2.3"
        if isinstance(d, str):
            normalized.append(d)
        else:
            # if someone used table forms, try to derive a string
            name = d.get("name") if isinstance(d, dict) else None
            if name:
                # pin/version may be in extra fields; keep simple
                normalized.append(name)
    return normalized


def main() -> None:
    base = Path(__file__).parent
    pyproject_path = base / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found next to setup.py")

    pyproject = _load_pyproject(pyproject_path)
    project = pyproject.get("project", {})

    name = project.get("name")
    version = project.get("version")
    description = project.get("description")
    python_requires = project.get("requires-python")
    dependencies = _normalize_dependencies(project.get("dependencies"))

    author, author_email = _first_maintainer(project.get("maintainers"))

    long_description, long_description_content_type = _read_readme(project, base)

    # tool.setuptools metadata (optional) — read but do not mutate the parsed pyproject mapping.
    tool_section = pyproject.get("tool", {})
    setuptools_tool = tool_section.get("setuptools", {}) if isinstance(tool_section, dict) else {}

    # Use values from pyproject if present; otherwise fall back to sensible defaults.
    # Convert to concrete types to avoid surprises later, but do NOT modify the original mapping.
    packages = list(setuptools_tool.get("packages") or ["quickscore"])
    package_dir = dict(setuptools_tool.get("package-dir") or {"quickscore": "src"})

    # Import setuptools inside main to avoid import-time side effects for tools that only inspect this file.
    from setuptools import setup  # type: ignore

    setup_kwargs: Dict[str, Any] = {
        "name": name or "quickscore",
        "version": version or "0.0.0",
        "description": description or "",
        "long_description": long_description,
        "long_description_content_type": long_description_content_type,
        "python_requires": python_requires or ">=3.12",
        "install_requires": dependencies,
        "packages": packages,
        "package_dir": package_dir,
        "include_package_data": True,
        # Minimal classifiers; do not claim a license if not present in pyproject.
        "classifiers": [
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
        ],
    }

    if author:
        setup_kwargs["author"] = author
    if author_email:
        setup_kwargs["author_email"] = author_email

    # If there is a __main__ entrypoint, some tools expect a console script. This is optional.
    # Uncomment and adapt the following block if you want to expose a CLI entrypoint:
    #
    # setup_kwargs.setdefault("entry_points", {}).setdefault("console_scripts", []).append(
    #     "quickscore=quickscore.__main__:main"
    # )

    setup(**setup_kwargs)


if __name__ == "__main__":
    main()
