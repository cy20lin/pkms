import sys
import winreg
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DispatcherStatus:
    installed: bool
    managed_by_pkms: bool = False
    executable_path: Optional[str] = None
    command: Optional[str] = None


class WindowsDispatcherInstaller:
    """
    Install / query / uninstall pkms:// URI dispatcher on Windows.

    Scope:
    - HKCU only
    - scheme: pkms
    - command: pkms.exe dispatch "%1"
    """

    SCHEME = "pkms"
    REG_BASE = "Software\\Classes\\pkms"
    MANAGED_MARKER_KEY = "pkms.managed_by"
    MANAGED_MARKER_VALUE = "pkms"

    def __init__(self, executable_path: Optional[Path] = None):
        self.executable_path = (executable_path or Path(sys.executable)).resolve()

    # ---------- helpers ----------

    def _open_key(self, subkey: str, writable=False):
        access = winreg.KEY_WRITE if writable else winreg.KEY_READ
        return winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            subkey,
            0,
            access,
        )

    def _create_key(self, subkey: str):
        return winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey)

    def _command_string(self) -> str:
        # IMPORTANT: "%1" must be quoted
        return f'"{self.executable_path}" cli dispatch "%1"'

    # ---------- public API ----------

    def install(self) -> None:
        """
        Install or overwrite pkms:// dispatcher.
        """
        # Root key
        with self._create_key(self.REG_BASE) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "URL:PKMS Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
            winreg.SetValueEx(
                key,
                self.MANAGED_MARKER_KEY,
                0,
                winreg.REG_SZ,
                self.MANAGED_MARKER_VALUE,
            )

        # Command
        with self._create_key(self.REG_BASE + "\\shell\\open\\command") as cmdkey:
            winreg.SetValueEx(
                cmdkey,
                "",
                0,
                winreg.REG_SZ,
                self._command_string(),
            )

    def status(self) -> DispatcherStatus:
        """
        Inspect current dispatcher state without modifying anything.
        """
        try:
            with self._open_key(self.REG_BASE) as key:
                try:
                    managed_by, _ = winreg.QueryValueEx(
                        key, self.MANAGED_MARKER_KEY
                    )
                except FileNotFoundError:
                    managed_by = None
        except FileNotFoundError:
            return DispatcherStatus(installed=False)

        try:
            with self._open_key(
                self.REG_BASE + "\\shell\\open\\command"
            ) as cmdkey:
                command, _ = winreg.QueryValueEx(cmdkey, "")
        except FileNotFoundError:
            command = None

        return DispatcherStatus(
            installed=True,
            managed_by_pkms=(managed_by == self.MANAGED_MARKER_VALUE),
            executable_path=str(self.executable_path),
            command=command,
        )

    def is_installed(self) -> bool:
        return self.status().installed

    def uninstall(self, *, force: bool = False) -> bool:
        """
        Remove dispatcher if and only if managed by pkms.
        Returns True if removed, False if nothing done.
        """
        try:
            with self._open_key(self.REG_BASE) as key:
                try:
                    managed_by, _ = winreg.QueryValueEx(
                        key, self.MANAGED_MARKER_KEY
                    )
                except FileNotFoundError:
                    managed_by = None
        except FileNotFoundError:
            return False

        if managed_by != self.MANAGED_MARKER_VALUE and not force:
            raise RuntimeError(
                "pkms dispatcher is not managed by this installation"
            )

        # Delete deepest keys first (Windows requirement)
        self._delete_key_safe(self.REG_BASE + "\\shell\\open\\command")
        self._delete_key_safe(self.REG_BASE + "\\shell\\open")
        self._delete_key_safe(self.REG_BASE + "\\shell")
        self._delete_key_safe(self.REG_BASE)

        return True

    # ---------- internal ----------

    def _delete_key_safe(self, subkey: str) -> None:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, subkey)
        except FileNotFoundError:
            pass
