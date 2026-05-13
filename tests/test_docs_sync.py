from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_pinned_sansad_tag_matches_requirements() -> None:
    readme = read_text(README_PATH)
    requirements = read_text(REQUIREMENTS_PATH)

    readme_match = re.search(r"pinned at `(v[0-9][^`]+)` in", readme)
    requirements_match = re.search(
        r"sansad-semantic-crawler\[http,pdf\]\s+@\s+git\+https://github\.com/CommonerLLP/"
        r"sansad-semantic-crawler\.git@(v[0-9][^\s]+)",
        requirements,
    )

    assert readme_match, "README should name the pinned sansad-semantic-crawler tag"
    assert requirements_match, "requirements.txt should pin sansad-semantic-crawler by tag"
    assert readme_match.group(1) == requirements_match.group(1)


def test_readme_make_commands_exist_in_makefile() -> None:
    readme = read_text(README_PATH)
    makefile = read_text(MAKEFILE_PATH)

    documented_targets = set(re.findall(r"make ([a-z0-9-]+)", readme))
    actual_targets = set(
        match.group(1)
        for match in re.finditer(r"^([a-z0-9-]+):", makefile, flags=re.MULTILINE)
        if not match.group(1).startswith(".")
    )

    missing = documented_targets - actual_targets
    assert not missing, f"README documents make targets missing from Makefile: {sorted(missing)}"


def test_readme_mentions_current_corpus_artifacts() -> None:
    readme = read_text(README_PATH)

    expected_paths = {
        "assets/parliament_libraries.js",
        "topics/libraries.json",
        "data/_parliament_libraries/manifest.jsonl",
        "data/_parliament_libraries/analysis.jsonl",
        "data/_parliament_libraries/_runs.jsonl",
    }

    missing = {path for path in expected_paths if path not in readme}
    assert not missing, f"README should mention corpus artifacts: {sorted(missing)}"


def test_readme_named_corpus_artifacts_exist() -> None:
    artifact_paths = [
        REPO_ROOT / "assets/parliament_libraries.js",
        REPO_ROOT / "topics/libraries.json",
        REPO_ROOT / "data/_parliament_libraries/manifest.jsonl",
        REPO_ROOT / "data/_parliament_libraries/analysis.jsonl",
        REPO_ROOT / "data/_parliament_libraries/_runs.jsonl",
    ]

    missing = [str(path.relative_to(REPO_ROOT)) for path in artifact_paths if not path.exists()]
    assert not missing, f"Documented corpus artifacts missing from repo: {missing}"
