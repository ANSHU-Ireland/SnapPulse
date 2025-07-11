#!/usr/bin/env python3
"""Copilot Charm for SnapPulse."""

from ops.main import main
from ops.charm import CharmBase
from ops.pebble import Layer
from ops.model import ActiveStatus


class CopilotCharm(CharmBase):
    """Charm the Copilot service."""

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
                "summary": "Copilot",
                "services": {
                    "copilot": {
                        "override": "replace",
                        "command": "uvicorn main:app --host 0.0.0.0 --port 8001",
                        "startup": "enabled",
                    }
                },
            }
        )
        self.unit.get_container("copilot").add_layer("copilot", layer, combine=True)
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(CopilotCharm)

    def _on_config_changed(self, event):
        """Handle config-changed event."""
        self._update_layer()

    def _update_layer(self):
        """Update the Pebble layer."""
        container = self.unit.get_container("copilot")

        if not container.can_connect():
            logger.info("Waiting for Pebble API")
            return

        # Define the layer
        pebble_layer = {
            "summary": "copilot layer",
            "description": "pebble config layer for copilot",
            "services": {
                "copilot": {
                    "override": "replace",
                    "summary": "copilot service",
                    "command": "python3 main.py",
                    "startup": "enabled",
                    "environment": {
                        "PORT": "8001",
                        "GITHUB_TOKEN": self.config.get("github-token", ""),
                    },
                }
            },
        }

        # Add the layer to Pebble
        container.add_layer("copilot", pebble_layer, combine=True)
        container.autostart()

        self.unit.status = ActiveStatus("Copilot service is running on port 8001")
        self._stored.started = True


if __name__ == "__main__":
    main(CopilotCharm)
