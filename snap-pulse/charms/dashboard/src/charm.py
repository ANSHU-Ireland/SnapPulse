#!/usr/bin/env python3
"""Dashboard Charm for SnapPulse."""

from ops.main import main
from ops.charm import CharmBase
from ops.pebble import Layer
from ops.model import ActiveStatus


class DashboardCharm(CharmBase):
    """Charm the Dashboard service."""

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
                "summary": "Dashboard",
                "services": {
                    "dashboard": {
                        "override": "replace",
                        "command": "npm start",
                        "startup": "enabled",
                    }
                },
            }
        )
        self.unit.get_container("dashboard").add_layer("dashboard", layer, combine=True)
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(DashboardCharm)

    def _on_config_changed(self, event):
        """Handle config-changed event."""
        self._update_layer()

    def _update_layer(self):
        """Update the Pebble layer."""
        container = self.unit.get_container("dashboard")

        if not container.can_connect():
            logger.info("Waiting for Pebble API")
            return

        # Define the layer
        pebble_layer = {
            "summary": "dashboard layer",
            "description": "pebble config layer for dashboard",
            "services": {
                "dashboard": {
                    "override": "replace",
                    "summary": "dashboard service",
                    "command": "npm start",
                    "startup": "enabled",
                    "environment": {
                        "PORT": "3000",
                        "API_URL": self.config.get("api-url", "http://api:8000"),
                    },
                }
            },
        }

        # Add the layer to Pebble
        container.add_layer("dashboard", pebble_layer, combine=True)
        container.autostart()

        self.unit.status = ActiveStatus("Dashboard service is running on port 3000")
        self._stored.started = True


if __name__ == "__main__":
    main(DashboardCharm)
