"""Device driver abstraction.

Two transports, one interface:
  - pyez : real JunOS device via Juniper PyEZ (NETCONF over SSH)
  - mock : file-backed fake JunOS device for testing (mock_state/<host>.set)

The mock lets the whole automation flow (render -> deploy -> compliance)
run end-to-end on this VM, which has no KVM and no JunOS images.
Point the same code at real devices by switching --transport pyez.
"""
import os
from abc import ABC, abstractmethod

from . import BASE
from .render import normalize_set_config


class Driver(ABC):
    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def get_running_set(self) -> str:
        """Return running config in 'display set' format."""
        ...

    @abstractmethod
    def load_set(self, config_text: str):
        """Load candidate config (set-format, merged)."""
        ...

    @abstractmethod
    def diff(self) -> str:
        """Diff candidate vs running ('+' adds, '-' removes)."""
        ...

    @abstractmethod
    def commit(self):
        ...

    @abstractmethod
    def close(self):
        ...


class PyEZDriver(Driver):
    """Real JunOS device via Juniper PyEZ."""

    def __init__(self, host, user, password=None, key_file=None, timeout=30):
        self.host = host
        self.user = user
        self.password = password
        self.key_file = key_file
        self.timeout = timeout
        self.dev = None
        self.cu = None

    def connect(self):
        from jnpr.junos import Device
        from jnpr.junos.utils.config import Config

        kwargs = {"host": self.host, "user": self.user, "timeout": self.timeout}
        if self.key_file:
            kwargs["ssh_private_key_file"] = self.key_file
        elif self.password:
            kwargs["password"] = self.password
        self.dev = Device(**kwargs)
        self.dev.open()
        self.cu = Config(self.dev)

    def get_running_set(self):
        out = self.dev.cli("show configuration | display set", warning=False)
        return out or ""

    def load_set(self, config_text):
        self.cu.lock()
        try:
            self.cu.load(config_text, format="set", merge=True)
        except Exception:
            self.cu.unlock()
            raise

    def diff(self):
        return self.cu.diff() or "(no differences)"

    def commit(self):
        try:
            self.cu.commit()
        finally:
            self.cu.unlock()

    def rollback(self):
        try:
            self.cu.rollback()
        finally:
            self.cu.unlock()

    def close(self):
        if self.dev is not None:
            self.dev.close()
            self.dev = None


class MockDriver(Driver):
    """File-backed fake JunOS device. State lives in mock_state/<hostname>.set."""

    STATE_DIR = BASE / "mock_state"

    def __init__(self, hostname):
        self.hostname = hostname
        self._path = self.STATE_DIR / f"{hostname}.set"
        self.staged = None

    def connect(self):
        pass

    def _running(self):
        if not self._path.exists():
            return set()
        return set(normalize_set_config(self._path.read_text()))

    def get_running_set(self):
        lines = sorted(self._running())
        return ("\n".join(lines) + "\n") if lines else ""

    def load_set(self, config_text):
        self.staged = set(normalize_set_config(config_text))

    def diff(self):
        if self.staged is None:
            return "(nothing loaded)"
        running = self._running()
        adds = sorted(self.staged - running)
        dels = sorted(running - self.staged)
        out = [f"+ {l}" for l in adds] + [f"- {l}" for l in dels]
        return "\n".join(out) if out else "(no differences)"

    def commit(self):
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)
        lines = sorted(self.staged or set())
        self._path.write_text(("\n".join(lines) + "\n") if lines else "")
        self.staged = None

    def close(self):
        pass


def get_driver(transport, device, user=None, password=None, key_file=None):
    if transport == "mock":
        return MockDriver(device["hostname"])
    if transport == "pyez":
        user = user or os.environ.get("NETAUTO_USER")
        password = password or os.environ.get("NETAUTO_PASSWORD")
        key_file = key_file or os.environ.get("NETAUTO_KEY_FILE")
        if not user:
            raise ValueError("pyez transport needs --user or NETAUTO_USER")
        return PyEZDriver(device["mgmt_ip"], user, password=password, key_file=key_file)
    raise ValueError(f"unknown transport: {transport}")
