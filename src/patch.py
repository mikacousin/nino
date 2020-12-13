# -*- coding: utf-8 -*-
# niño
# Copyright (c) 2020 Mika Cousin <mika.cousin@gmail.com>
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
import copy

from nino.device import Device
from nino.defines import App
from nino.tab_patch import update_channels_list
from nino.undo_redo import undoable


class Patch:
    """Channels associate with devices

    Attributes:
        app: Gio.Application
        channels (dic): each channel can have multiple devices with same fixture
    """

    def __init__(self):
        self.channels = {}

    @undoable
    def patch_channel(self, channel, output, universe, fixture):
        """Patch channel

        Args:
            channel (int): Channel [1 - MAX_CHANNELS]
            output (int): Output [1 - 512]
            universe (int): Universe
            fixture (Fixture): fixture to use
        """
        # Channel already patched
        if channel in self.channels:
            # Depatch
            if output == 0:
                # Reset device's dmx output
                for device in self.channels[channel].values():
                    for name in device.parameters.keys():
                        device.parameters[name] = 0
                    device.send_dmx()
                del self.channels[channel]
                App().tabs.get("live").channels[channel - 1].device = None
                return
            # Patch new device
            device = Device(channel, output, universe, fixture)
            self.channels[channel] = {}
            self.channels[channel][f"{output}.{universe}"] = device
            device.send_dmx()
        else:
            # New patch, create device
            device = Device(channel, output, universe, fixture)
            self.channels[channel] = {}
            self.channels[channel][f"{output}.{universe}"] = device
            device.send_dmx()
        App().tabs.get("live").channels[channel - 1].device = device

    @undoable
    def insert_output(self, channel, output, universe, fixture):
        """Insert Output

        Args:
            channel (int): Channel [1 - MAX_CHANNELS]
            output (int): Output [1 - 512]
            universe (int): Universe
            fixture (Fixture): fixture to use
        """
        if channel in self.channels:
            # Channel already patched
            device = Device(channel, output, universe, fixture)
            self.channels[channel][f"{output}.{universe}"] = device
            device.send_dmx()
        else:
            # New patch, create device
            device = Device(channel, output, universe, fixture)
            self.channels[channel] = {}
            self.channels[channel][f"{output}.{universe}"] = device
            device.send_dmx()

    # pylint: disable=no-self-use
    def do(self, command):
        """Execute command

        Args:
            command: command to execute

        Returns:
            command result
        """
        return App().undo_manager.do(command)

    def undo(self):
        """Update views after undo."""
        if App().tabs.get("patch"):
            App().tabs.get("patch").sacn.update_view()
            model = App().tabs.get("patch").treeview.get_model()
            App().tabs.get("patch").treeview.get_selection().unselect_all()
            for row in model:
                channel = row[0]
                outputs = self.channels.get(channel)
                if outputs:
                    for device in outputs.values():
                        output = device.output
                        universe = device.universe
                        footprint = device.footprint
                        update_channels_list(
                            f"{output}.{universe}", footprint, channel, model, row.path
                        )
                else:
                    row[1] = ""
                    row[2] = ""
        App().tabs.get("live").flowbox.invalidate_filter()

    def redo(self):
        """Update views after redo."""
        self.undo()

    def copy(self):
        """
        Returns:
            a copy of patch object
        """
        patch = Patch()
        # Need deepcopy for channels with several outputs
        patch.channels = copy.deepcopy(self.channels)
        return patch

    def restore(self, patch):
        """Restore patch to the previous state.

        Args:
            patch: patch object
        """
        self.channels = patch.channels
