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

    def test_pytest_basetemp_and_options_contract(self):
        pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIsNotNone(tomllib, "tomllib/tomli required for pyproject validation")
        data = tomllib.loads(pyproject_text)

        project = data["project"]
        self.assertEqual(project["version"] if "version" in project else None, None)
        urls = project["urls"]
        for key in ("Contributing", "Security", "Code of Conduct"):
            self.assertIn(key, urls, f"Missing project.urls key: {key}")

        dev_deps = project.get("optional-dependencies", {}).get("dev", [])
        self.assertTrue(any(d.startswith("pytest") for d in dev_deps))
        self.assertTrue(any(d.startswith("ruff") for d in dev_deps))

        pytest_opts = data["tool"]["pytest"]["ini_options"]
        addopts = pytest_opts.get("addopts", "")
        self.assertIn("--strict-markers", addopts)
        self.assertNotIn("--basetemp", addopts, "Relative --basetemp in addopts is forbidden (T-20261114-932985855)")
        self.assertTrue(pytest_opts.get("xfail_strict"))
        self.assertNotIn("asyncio_default_fixture_loop_scope", pytest_opts, "pytest-asyncio is not a dependency")
        norecurse = pytest_opts.get("norecursedirs", [])
        for expected in (".*", "venv", "node_modules", ".pytest_temp"):
            self.assertIn(expected, norecurse)

    def test_gitignore_hygiene_and_privacy_defense(self):
        content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in (
            ".pytest_temp/",
            ".pytest_tmp*/",
            "*MARKETING-LOG.txt",
            "TO-DECIDE-USER*",
            "TASKPLAN_*.md",
            "*.db-wal",
            "*.sqlite-wal",
            "tmpclaude-*",
        ):
            self.assertIn(pattern, content, f".gitignore missing pattern: {pattern}")

    def test_dependabot_and_issue_templates(self):
        dependabot = REPO_ROOT / ".github" / "dependabot.yml"
        self.assertTrue(dependabot.exists(), ".github/dependabot.yml must exist")
        dep_text = dependabot.read_text(encoding="utf-8")
        self.assertIn('package-ecosystem: "github-actions"', dep_text)
        self.assertIn('package-ecosystem: "pip"', dep_text)

        tpl_dir = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
        for name in ("config.yml", "bug_report.md", "feature_request.md"):
            self.assertTrue((tpl_dir / name).exists(), f"Missing issue template: {name}")

        tests_wf = (REPO_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertIn("python -m pip check", tests_wf)
        self.assertIn("python -m pip install --no-build-isolation --dry-run .", tests_wf)

    def test_p022_and_governance_files_present(self):
        required = (
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "SKILL.md",
            "llms.txt",
            "llm.txt",
        )
        for rel in required:
            path = REPO_ROOT / rel
            self.assertTrue(path.exists(), f"Missing required file: {rel}")
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("_Local_DEV", text, f"Forbidden host path in {rel}")
            self.assertNotIn("OneDrive", text, f"Forbidden personal OneDrive path in {rel}")

        coc = (REPO_ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
        self.assertIn("Contributor Covenant", coc)
        self.assertIn("## Deutsch", coc)

        sec = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("security/advisories/new", sec)
        # ellmos.ai / open-bricks.org do not resolve, lukasgeiger.com has no MX (ellmos-ai/ellmos-homebase-mcp#21)
        dead = ("security@ellmos.ai", "security@open-bricks.org", "lukas@open-bricks.org", "support@lukasgeiger.com")
        for rel in required:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            for address in dead:
                self.assertNotIn(address, text, f"{rel} still advertises {address}")
        self.assertIn("48 hours", sec)
        self.assertIn("48 Stunden", sec)

        skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("rinnsal 0.1.0", skill)

        llm_compat = (REPO_ROOT / "llm.txt").read_text(encoding="utf-8")
        self.assertIn("llms.txt", llm_compat)

    def test_manifest_in_includes_governance_and_p022(self):
        manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        expected = (
            "LICENSE",
            "THIRD_PARTY_LICENSES.md",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "SKILL.md",
            "llms.txt",
            "llm.txt",
            "CHANGELOG.md",
            "README.md",
            "README_de.md",
            "README_es.md",
            "README_zh.md",
            "README_ja.md",
            "README_ru.md",
            "README_fr.md",
            "README_hi.md",
            "README_ar.md",
            "README_bn.md",
            "README_pt.md",
        )
        for item in expected:
            self.assertIn(item, manifest, f"MANIFEST.in missing: {item}")

    def test_readme_and_llms_link_governance_and_p022(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        llms = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")

        for target in ("SKILL.md", "llms.txt", "llm.txt", "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md"):
            self.assertIn(target, readme_en, f"README.md missing link to {target}")
            self.assertIn(target, readme_de, f"README_de.md missing link to {target}")
            self.assertIn(target, llms, f"llms.txt missing reference to {target}")


if __name__ == "__main__":
    unittest.main()
