import tempfile
import unittest
from pathlib import Path

from desktop_launcher import user_data_directory


class UserDataDirectoryTests(unittest.TestCase):
    def test_macos_uses_application_support(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            result = user_data_directory("darwin", {}, home)
            self.assertEqual(
                result,
                home / "Library" / "Application Support" / "Gather RSVP",
            )
            self.assertTrue(result.is_dir())

    def test_windows_uses_local_app_data(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            result = user_data_directory(
                "win32",
                {"LOCALAPPDATA": str(home / "LocalAppData")},
                home,
            )
            self.assertEqual(result, home / "LocalAppData" / "Gather RSVP")

    def test_linux_respects_xdg_data_home(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            result = user_data_directory(
                "linux",
                {"XDG_DATA_HOME": str(home / "XDG")},
                home,
            )
            self.assertEqual(result, home / "XDG" / "gather-rsvp")
