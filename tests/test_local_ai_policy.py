import ast
from pathlib import Path


BLOCKED_CLOUD_AI_IMPORTS = {
    "openai",
    "anthropic",
    "google.generativeai",
    "azure.ai",
    "langsmith",
    "posthog",
    "sentry_sdk",
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)

    return modules


def test_backend_does_not_import_cloud_ai_or_telemetry_sdks():
    repo_root = Path(__file__).resolve().parents[1]
    python_files = [*repo_root.joinpath("app").rglob("*.py")]

    violations = []
    for path in python_files:
        for module in imported_modules(path):
            if any(module == blocked or module.startswith(f"{blocked}.") for blocked in BLOCKED_CLOUD_AI_IMPORTS):
                violations.append(f"{path.relative_to(repo_root)} imports {module}")

    assert violations == []
