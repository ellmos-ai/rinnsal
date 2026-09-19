# -*- coding: utf-8 -*-
"""Contract tests for repository metadata, CI workflows, licensing, and governance.

Validates:
- PEP 621 metadata in pyproject.toml
- Multi-OS and hardened GitHub Actions workflows
- Cloud-sync & canonical LOCK-System protection in .gitignore
- Statutory liability notice (§ 521 BGB Gefälligkeitsrecht)
- Third-party licenses & zero-runtime-dependencies audit
- UTF-8 file integrity
- Mermaid diagram syntax guardrails
- CLI smoke commands
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


class TestMetadataContract(unittest.TestCase):
    """Contract tests for repository hygiene, governance, and CI matrix."""

    def test_pep621_pyproject_structure(self):
        pyproject_path = REPO_ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml must exist in repo root")

        content = pyproject_path.read_text(encoding="utf-8")
        if tomllib:
            data = tomllib.loads(content)
            project = data.get("project", {})
            self.assertEqual(project.get("name"), "rinnsal")
            self.assertEqual(project.get("requires-python"), ">=3.10")
            self.assertEqual(project.get("license"), "MIT")
            license_files = project.get("license-files", [])
            self.assertIn("LICENSE", license_files)
            self.assertIn("THIRD_PARTY_LICENSES.md", license_files)

            urls = project.get("urls", {})
            required_urls = [
                "Homepage", "Repository", "Documentation", "Issues",
                "Changelog", "Third-Party Licenses", "Parent Organization", "LLM Ready"
            ]
            for key in required_urls:
                self.assertIn(key, urls, f"Missing required project.urls key: {key}")

            pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
            self.assertEqual(pytest_opts.get("testpaths"), ["tests"])
            self.assertEqual(pytest_opts.get("pythonpath"), ["."])

            ruff_opts = data.get("tool", {}).get("ruff", {})
            self.assertEqual(ruff_opts.get("target-version"), "py310")
        else:
            self.assertIn('name = "rinnsal"', content)
            self.assertIn('license = "MIT"', content)
            self.assertIn('license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]', content)
            self.assertIn('[project.urls]', content)
            self.assertIn('[tool.ruff]', content)

    def test_version_parity(self):
        import rinnsal
        version = rinnsal.__version__
        self.assertTrue(bool(re.match(r"^\d+\.\d+\.\d+", version)), f"Invalid semver: {version}")

        pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = {attr = "rinnsal.__version__"}', pyproject_text)

    def test_ci_workflow_hardening(self):
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        self.assertTrue(workflows_dir.exists(), ".github/workflows directory must exist")

        workflows = list(workflows_dir.glob("*.yml"))
        self.assertGreaterEqual(len(workflows), 3, "Expected at least 3 workflow files")

        for wf in workflows:
            content = wf.read_text(encoding="utf-8")
            self.assertIn("permissions:", content, f"{wf.name} missing explicit permissions block")
            self.assertIn("concurrency:", content, f"{wf.name} missing concurrency control")
            self.assertIn("timeout-minutes:", content, f"{wf.name} missing timeout-minutes limit")

        # Specific checks for tests.yml
        tests_wf = (workflows_dir / "tests.yml").read_text(encoding="utf-8")
        self.assertIn("ubuntu-latest", tests_wf, "tests.yml must test on ubuntu-latest")
        self.assertIn("windows-latest", tests_wf, "tests.yml must test on windows-latest")
        for py_ver in ["3.10", "3.11", "3.12", "3.13"]:
            self.assertIn(py_ver, tests_wf, f"tests.yml missing Python {py_ver} in matrix")
        self.assertIn("pytest", tests_wf, "tests.yml should run pytest")
        self.assertIn("ruff check", tests_wf, "tests.yml should run ruff static analysis")

    def test_gitignore_multihost_and_locks(self):
        gitignore_path = REPO_ROOT / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore must exist")
        content = gitignore_path.read_text(encoding="utf-8")

        # Multi-host sync exclusions
        self.assertIn("*conflicted copy*", content)
        self.assertIn("*-ASUS*", content)
        self.assertIn("*-WORKSTATION*", content)
        self.assertIn("*-Mac Studio*", content)

        # Canonical lock patterns
        self.assertIn("LOCK", content)
        self.assertIn("LOCK.*", content)
        self.assertIn("LOCK*.txt", content)
        self.assertIn("LOCK.permissions.json", content)
        self.assertIn("LOCK.user.*", content)
        self.assertIn("LOCK.until.*", content)
        self.assertIn("LOCK.condition.*", content)

        # Zero runtime dependencies lockfiles
        self.assertIn("uv.lock", content)

    def test_bgb_liability_notice(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

        self.assertIn("521 BGB", readme_en, "README.md must cite § 521 BGB statutory liability")
        self.assertIn("521 BGB", readme_de, "README_de.md must cite § 521 BGB statutory liability")
        self.assertIn("Gefälligkeitsrecht", readme_en + readme_de, "Liability section must reference Gefälligkeitsrecht")

    def test_third_party_licenses_audit(self):
        tpl_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
        self.assertTrue(tpl_path.exists(), "THIRD_PARTY_LICENSES.md must exist")
        content = tpl_path.read_text(encoding="utf-8")

        self.assertIn("PSF-2.0", content)
        self.assertIn("MIT", content)
        self.assertIn("Zero External Runtime Dependencies", content)
        self.assertIn("RunAsInvoker", content)
        for inv in ["INV-LOCAL-01", "INV-SEC-04", "INV-SEC-05", "INV-SLA-10"]:
            self.assertIn(inv, content, f"Missing governance invariant: {inv}")

    def test_utf8_integrity(self):
        text_extensions = {".py", ".md", ".toml", ".yml", ".json", ".txt"}
        for ext in text_extensions:
            for file_path in REPO_ROOT.rglob(f"*{ext}"):
                if any(part.startswith(".") or part in {"build", "dist", "__pycache__", "_after-care"} for part in file_path.parts):
                    continue
                try:
                    file_path.read_text(encoding="utf-8")
                except UnicodeDecodeError as exc:
                    self.fail(f"File {file_path} failed UTF-8 decode: {exc}")

    def test_mermaid_diagram_syntax(self):
        mermaid_block_pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
        for md_file in REPO_ROOT.rglob("*.md"):
            if any(part.startswith(".") or part in {"build", "dist", "_after-care"} for part in md_file.parts):
                continue
            content = md_file.read_text(encoding="utf-8")
            for block in mermaid_block_pattern.findall(content):
                lines = block.strip().splitlines()
                is_sequence = any("sequenceDiagram" in item for item in lines)
                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("%%"):
                        continue
                    if is_sequence:
                        self.assertFalse(
                            stripped.endswith(";") and not stripped.startswith("participant"),
                            f"Mermaid sequence diagram line in {md_file.name} ends with ';': {stripped}"
                        )

    def test_cli_smoke(self):
        from rinnsal.cli import main
        # --help exits with 0 via SystemExit or returns 0
        with self.assertRaises(SystemExit) as cm:
            main(["--help"])
        self.assertEqual(cm.exception.code, 0)

        with self.assertRaises(SystemExit) as cm:
            main(["--version"])
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
