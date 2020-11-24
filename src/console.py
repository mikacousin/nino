#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Niño
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
import sacn

from nino.defines import UNIVERSES


class Fixture:
    """A fixture is a template device"""

    def __init__(self, name):
        self.name = name
        self.manufacturer = ""
        self.model_name = ""
        self.parameters = {
            "Intensity": {
                "number": 0,
                "type": "HTP8",
                "offset": {"Hight Byte": 0, "Low Byte": 0, "Step": 4},
                "default": 0,
                "highligt": 255,
                "range": {"Minimum": 0, "Maximum": 0, "Percent": True},
            }
        }
        self.modes = []


class Device:
    """A device is a patched fixture"""

    def __init__(self, channel, output, universe, fixture):
        self.channel = channel
        if output is not None:
            self.output = output
        self.universe = universe
        self.fixture = fixture
        self.parameters = {}
        self.footprint = 0
        for param in self.fixture.parameters.values():
            self.parameters[param.get("number")] = param.get("default")
            param_type = param.get("type")
            if param_type in ("HTP8", "LTP8"):
                self.footprint += 1
            elif param_type in ("HTP16", "LTP16"):
                self.footprint += 2
            else:
                print("Device parameter type '{param_type}' not supported")
                print("Supported types are : HTP8, LTP8, HTP16, LTP16")


class Patch:
    """Channels associate with devices"""

    def __init__(self):
        self.channels = {}

    def patch_channel(self, channel, output, universe, fixture):
        """Patch channel

        Args:
            channel (int): Channel [1-MAX_CHANNELS]
            output (int): Output [1-512]
            universe (int): Universe
            fixture (Fixture): fixture to use

        Returns:
            Device footprint (int)
        """
        if channel in self.channels:
            # Channel already patched
            self.channels[channel].output = output
            self.channels[channel].universe = universe
            if self.channels[channel].fixture is not fixture:
                self.channels[channel].fixture = fixture
                self.channels[channel].parameters = {}
                for param in fixture.parameters.values():
                    self.channels[channel].parameters[param.get("number")] = param.get(
                        "default"
                    )
        else:
            # New patch, create device
            device = Device(channel, output, universe, fixture)
            self.channels[channel] = device
        return self.channels[channel].footprint


class Console:
    """Application's heart"""

    def __init__(self):
        # Dimmer fixture at index 0
        self.fixtures = []
        dimmer = Fixture("Dimmer")
        self.fixtures.append(dimmer)

        self.patch = Patch()

        # Start sACN sender
        self.sender = sacn.sACNsender()
        self.sender.start()
        for universe in UNIVERSES:
            self.sender.activate_output(universe)
            self.sender[universe].multicast = True
