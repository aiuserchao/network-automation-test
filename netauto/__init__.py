"""netauto - Juniper (JunOS) network automation toolkit.

Inventory (JSON) -> Jinja2 templates -> driver (PyEZ/NETCONF or mock) ->
deploy + compliance check. Operated by Muse via chat.
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

__version__ = "0.1.0"
