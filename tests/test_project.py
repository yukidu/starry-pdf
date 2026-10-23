from __future__ import annotations
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("source_prep", ROOT / "scripts" / "prepare_source.py")
assert SPEC and SPEC.loader
source_prep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source_prep)

def git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()

class TestLicense(unittest.TestCase):
    def test_expected_paths(self):
        text = "MIT License\nCopyright (c) 2025 Stirling PDF Inc.\n" + "\n".join(
            f'All content under "{p}/" requires a separate license'
            for p in source_prep.EXPECTED_EXCLUDED
        )
        self.assertEqual(source_prep.check_upstream_license(text), source_prep.EXPECTED_EXCLUDED)

    def test_license_change_fails_closed(self):
        with self.assertRaises(ValueError):
            source_prep.check_upstream_license('MIT License\nCopyright (c) 2025 Stirling PDF Inc.\n"engine/"')

    def test_local_fixture_excludes_restricted_directories(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            origin = root / "origin"
            origin.mkdir()
            git("init", "-b", "main", cwd=origin)
            git("config", "user.name", "CI", cwd=origin)
            git("config", "user.email", "ci@example.invalid", cwd=origin)
            license_text = "MIT License\nCopyright (c) 2025 Stirling PDF Inc.\n" + "\n".join(
                f'All content under "{p}/" requires a separate license' for p in source_prep.EXPECTED_EXCLUDED
            )
            (origin / "LICENSE").write_text(license_text)
            (origin / "README.md").write_text("Allowed code\n")
            (origin / "allowed").mkdir()
            (origin / "allowed" / "x.txt").write_text("MIT licensed")
            for path in source_prep.EXPECTED_EXCLUDED:
                restricted = origin / path
                restricted.mkdir(parents=True, exist_ok=True)
                (restricted / "secret.txt").write_text("DO NOT COPY")
            git("add", ".", cwd=origin)
            git("commit", "-m", "fixture", cwd=origin)
            git("tag", "v3.2.1", cwd=origin)
            sha = git("rev-parse", "HEAD", cwd=origin)
            destination = root / "vendor" / "stirling-pdf"
            audit = source_prep.source_copy(origin.as_uri(), "v3.2.1", sha, destination)
            self.assertEqual(audit["commit"], sha)
            self.assertTrue((destination / "allowed" / "x.txt").exists())
            self.assertFalse((destination / ".git").exists())
            for path in source_prep.EXPECTED_EXCLUDED:
                self.assertFalse((destination / path).exists())
            with self.assertRaises(FileExistsError):
                source_prep.source_copy(origin.as_uri(), "v3.2.1", sha, destination)

class TestPWA(unittest.TestCase):
    def test_manifest(self):
        manifest = json.loads((ROOT / "launchpad" / "manifest.webmanifest").read_text())
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["start_url"], "/install")
        for icon in manifest["icons"]:
            self.assertTrue((ROOT / "launchpad" / icon["src"].lstrip("/")).is_file())

    def test_local_only(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        self.assertIn("127.0.0.1:8088:80", compose)
        self.assertIn('SECURITY_ENABLELOGIN: "true"', compose)

    def test_no_caching_user_documents(self):
        sw = (ROOT / "launchpad" / "sw.js").read_text()
        self.assertNotIn("caches.open", sw)
        self.assertNotIn("addEventListener('fetch'", sw)
