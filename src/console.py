# -*- coding: utf-8 -*-
# niño
# Copyright (c) 2020-2021 Mika Cousin <mika.cousin@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import json
import os
import sacn

from gi.repository import GLib

from nino.defines import App, UNIVERSES
from nino.fixture import Fixture
from nino.patch import Patch
from nino.paths import get_fixtures_dir
from nino.undo_redo import UndoManager


class DMX:
    """DMX levels"""

    def __init__(self):
        self.levels = {}
        for universe in UNIVERSES:
            self.levels[universe] = [0] * 512

    def flush(self, universe):
        """Flush levels to sACN

        Args:
            universe (int): one in UNIVERSES
        """
        App().sender[universe].dmx_data = tuple(self.levels[universe])


# pylint: disable=too-many-instance-attributes
class Console:
    """Application's heart"""

    def __init__(self):
        self.tabs = {}
        # Dimmer fixture at index 0
        self.fixtures = []
        dimmer = Fixture("Dimmer")
        dimmer.model_name = "Dimmer"
        self.fixtures.append(dimmer)
        # Fixtures parameters groups
        self.fixtures_param_grps = load_fixtures_groups()

        self.patch = Patch()
        self.dmx = DMX()

        # Start sACN sender and receiver
        self.sender = sacn.sACNsender()
        self.sender.start()
        self.receiver = sacn.sACNreceiver()
        self.receiver.start()
        for universe in UNIVERSES:
            self.sender.activate_output(universe)
            self.sender[universe].multicast = True
            self.receiver.join_multicast(universe)
            self.receiver.register_listener(
                "universe", receive_packet, universe=universe
            )

        # Undo manager
        self.undo_manager = UndoManager()

    def console_exit(self):
        """Stop console"""
        self.sender.stop()
        self.receiver.stop()


def load_fixtures_groups():
    """Load fixtures groups

    Returns:
        dictionnary
    """
    path = get_fixtures_dir()
    with open(os.path.join(path, "groups.json"), "r") as groups_file:
        groups = json.load(groups_file)
    return groups


def receive_packet(_packet):
    """Callback when receive sACN packets

    Args:
        _packet (sacn.DataPacket): DMX data
    """
    if App().tabs.get("live"):
        # Update Live view
        GLib.idle_add(App().tabs.get("live").flowbox.queue_draw)
    if App().tabs.get("device_controls"):
        # Update Device Controls
        GLib.idle_add(App().tabs.get("device_controls").update_view)
