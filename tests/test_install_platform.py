#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Exercise the installer's actual platform/asset selection without downloading.

Run: python3 -m unittest discover -s tests -p 'test_install_platform.py' -v
No network or external services are substituted: only the local shell selection
blocks are evaluated, using release asset names as input.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


INSTALLER = (Path(__file__).resolve().parents[1] / "install.sh").read_text()
DETECTION = INSTALLER.split("# Helper: download a URL to stdout", 1)[0]
SELECTION = INSTALLER.split("# Match the correct binary from release assets.", 1)[1]
SELECTION = SELECTION.split('URL="https://github.com/', 1)[0]
HOST = os.uname() if hasattr(os, "uname") else None
ARCH = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64"}.get(HOST.machine if HOST else "")


@unittest.skipUnless(HOST and HOST.sysname == "Linux" and ARCH, "requires supported Linux host")
class InstallPlatformTests(unittest.TestCase):
    def select(self, variables=None, assets=None):
        env = os.environ.copy()
        for name in ("TERMUX_VERSION", "ANDROID_ROOT", "PREFIX", "TINA4_INSTALL_DIR"):
            env.pop(name, None)
        with tempfile.TemporaryDirectory() as home:
            env["HOME"] = home
            env.update(variables or {})
            env["LATEST"] = "v-test"
            env["RELEASE_JSON"] = json.dumps({"assets": [
                {"name": name} for name in (assets if assets is not None else [
                    f"tina4-linux-{ARCH}", f"tina4-linux-musl-{ARCH}",
                ])
            ]}, indent=2)
            result = subprocess.run(
                ["sh", "-c", DETECTION + SELECTION +
                 '\nprintf "%s\\n" "$PLATFORM" "$INSTALL_DIR" "$BINARY"\n'],
                env=env, text=True, capture_output=True,
            )
            return result, home

    def test_regular_linux_keeps_glibc_and_system_directory(self):
        result, _ = self.select()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "linux", "/usr/local/bin", f"tina4-linux-{ARCH}",
        ])

    def test_termux_uses_static_binary_and_prefix(self):
        result, _ = self.select({"TERMUX_VERSION": "0.118.3", "PREFIX": "/termux/usr"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "linux-musl", "/termux/usr/bin", f"tina4-linux-musl-{ARCH}",
        ])

    def test_android_without_termux_uses_user_directory(self):
        result, home = self.select({"ANDROID_ROOT": "/system"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "linux-musl", f"{home}/.local/bin", f"tina4-linux-musl-{ARCH}",
        ])

    def test_termux_without_prefix_uses_user_directory(self):
        result, home = self.select({"TERMUX_VERSION": "0.118.3"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[1], f"{home}/.local/bin")

    def test_explicit_directory_takes_precedence(self):
        for variables in ({}, {"TERMUX_VERSION": "0.118.3", "PREFIX": "/termux/usr"}):
            with self.subTest(variables=variables):
                result, _ = self.select({**variables, "TINA4_INSTALL_DIR": "/custom/bin"})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.splitlines()[1], "/custom/bin")

    def test_prefix_alone_does_not_mean_android(self):
        result, _ = self.select({"PREFIX": "/usr/local"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "linux")

    def test_empty_android_variables_do_not_mean_android(self):
        result, _ = self.select({"TERMUX_VERSION": "", "ANDROID_ROOT": ""})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "linux")

    def test_android_refuses_glibc_fallback_when_musl_missing(self):
        result, _ = self.select({"ANDROID_ROOT": "/system"}, [f"tina4-linux-{ARCH}"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No matching binary found for linux-musl/", result.stderr)


if __name__ == "__main__":
    unittest.main()
