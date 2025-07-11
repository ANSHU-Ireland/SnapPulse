#!/usr/bin/env python3

"""Charm for SnapPulse Dashboard service."""

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class DashboardCharm(CharmBase):
    """Charm the Dashboard service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(
            self.on.dashboard_pebble_ready, self._on_dashboard_pebble_ready
        )
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self._stored.set_default(started=False)

    def _on_dashboard_pebble_ready(self, event):
        """Handle pebble-ready event."""
        self._update_layer()

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
