#!/usr/bin/env python3
"""API Charm for SnapPulse."""

from ops.main import main
from ops.charm import CharmBase
from ops.pebble import Layer
from ops.model import ActiveStatus


class ApiCharm(CharmBase):
    """Charm the API service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_install(self, _):
        """Handle the install event."""
        self.unit.status = ActiveStatus("installing dependencies")

    def _on_config_changed(self, _):
        """Handle the config-changed event."""
        layer = Layer(
            {
                "summary": "API",
                "services": {
                    "api": {
                        "override": "replace",
                        "command": "uvicorn main:app --host 0.0.0.0 --port 8000",
                        "startup": "enabled",
                    }
                },
            }
        )
        self.unit.get_container("api").add_layer("api", layer, combine=True)
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(ApiCharm)
