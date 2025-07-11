#!/usr/bin/env python3

"""Charm for SnapPulse Collector service."""

import logging
import subprocess
import os

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class CollectorCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.collector_pebble_ready, self._on_collector_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self._stored.set_default(started=False)

    def _on_collector_pebble_ready(self, event):
        """Handle pebble-ready event."""
        self._update_layer()

    def _on_config_changed(self, event):
        """Handle config-changed event."""
        self._update_layer()

    def _update_layer(self):
        """Update the Pebble layer."""
        container = self.unit.get_container("collector")
        
        if not container.can_connect():
            logger.info("Waiting for Pebble API")
            return

        # Define the layer
        pebble_layer = {
            "summary": "collector layer",
            "description": "pebble config layer for collector",
            "services": {
                "collector": {
                    "override": "replace",
                    "summary": "collector service",
                    "command": "python3 /app/app.py",
                    "startup": "enabled",
                    "environment": {
                        "SNAP_NAME": self.config.get("snap-name", "firefox"),
                    },
                }
            },
        }

        # Add the layer to Pebble
        container.add_layer("collector", pebble_layer, combine=True)
        container.autostart()

        self.unit.status = ActiveStatus("Collector service is running")
        self._stored.started = True


if __name__ == "__main__":
    main(CollectorCharm)
