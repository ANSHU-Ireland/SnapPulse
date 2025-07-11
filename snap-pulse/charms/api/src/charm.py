#!/usr/bin/env python3

"""Charm for SnapPulse API service."""

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class ApiCharm(CharmBase):
    """Charm the API service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.api_pebble_ready, self._on_api_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self._stored.set_default(started=False)

    def _on_api_pebble_ready(self, event):
        """Handle pebble-ready event."""
        self._update_layer()

    def _on_config_changed(self, event):
        """Handle config-changed event."""
        self._update_layer()

    def _update_layer(self):
        """Update the Pebble layer."""
        container = self.unit.get_container("api")

        if not container.can_connect():
            logger.info("Waiting for Pebble API")
            return

        # Define the layer
        pebble_layer = {
            "summary": "api layer",
            "description": "pebble config layer for api",
            "services": {
                "api": {
                    "override": "replace",
                    "summary": "api service",
                    "command": "uvicorn main:app --host 0.0.0.0 --port 8000",
                    "startup": "enabled",
                    "environment": {
                        "PORT": "8000",
                    },
                }
            },
        }

        # Add the layer to Pebble
        container.add_layer("api", pebble_layer, combine=True)
        container.autostart()

        self.unit.status = ActiveStatus("API service is running on port 8000")
        self._stored.started = True


if __name__ == "__main__":
    main(ApiCharm)
