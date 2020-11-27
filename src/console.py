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

from nino.defines import App, UNIVERSES


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
                "offset": {"High Byte": 0, "Low Byte": 0, "Step": 4},
                "default": 0,
                "highligt": 255,
                "range": {"Minimum": 0, "Maximum": 0, "Percent": True},
            }
        }
        self.modes = []

    def get_footprint(self):
        """Return footprint

        Returns:
            footprint (int)
        """
        footprint = 0
        for param in self.parameters.values():
            param_type = param.get("type")
            if param_type in ("HTP8", "LTP8"):
                footprint += 1
            elif param_type in ("HTP16", "LTP16"):
                footprint += 2
            else:
                print("Device parameter type '{param_type}' not supported")
                print("Supported types are : HTP8, LTP8, HTP16, LTP16")
        return footprint


class Device:
    """A device is a patched fixture

    Attributes:
        channel (int): [1 - MAX_CHANNELS]
        output (int): [1 - 512]
        universe (int): universe
        fixture (Fixture): fixture
    """

    def __init__(self, channel, output, universe, fixture):
        self.channel = channel
        if output is not None:
            self.output = output
        self.universe = universe
        self.fixture = fixture
        self.parameters = {}
        self.footprint = 0
        for name, param in self.fixture.parameters.items():
            self.parameters[name] = param.get("default")
            param_type = param.get("type")
            if param_type in ("HTP8", "LTP8"):
                self.footprint += 1
            elif param_type in ("HTP16", "LTP16"):
                self.footprint += 2
            else:
                print("Device parameter type '{param_type}' not supported")
                print("Supported types are : HTP8, LTP8, HTP16, LTP16")

    def send_dmx(self):
        for name, value in self.parameters.items():
            param_type = self.fixture.parameters[name].get("type")
            offset = self.fixture.parameters[name].get("offset")
            if param_type in ("HTP8", "LTP8"):
                out = self.output + offset.get("High Byte") - 1
                if self.output:
                    val = (value >> 8) & 0xFF
                    App().dmx.levels[self.universe][out] = val
            elif param_type in ("HTP16", "LTP16"):
                out = self.output + offset.get("High Byte") - 1
                val = (value >> 8) & 0xFF
                out2 = self.output + offset.get("Low Byte") - 1
                val2 = value & 0xFF
                if self.output:
                    App().dmx.levels[self.universe][out] = val
                    App().dmx.levels[self.universe][out2] = val2
        if self.output:
            App().dmx.flush(self.universe)


class Patch:
    """Channels associate with devices

    Attributes:
        channels (dic): each channel can have multiple devices with same fixture
    """

    def __init__(self):
        self.channels = {}

    def patch_channel(self, channel, output, universe, fixture):
        """Patch channel

        Args:
            channel (int): Channel [1 - MAX_CHANNELS]
            output (int): Output [1 - 512]
            universe (int): Universe
            fixture (Fixture): fixture to use
        """
        if channel in self.channels:
            # Channel already patched
            if output == 0:
                # Depatch
                del self.channels[channel]
                return
            if f"{output}.{universe}" in self.channels[channel]:
                device = self.channels[channel][f"{output}.{universe}"]
                device.output = output
                device.universe = universe
                if device.fixture is not fixture:
                    device.fixture = fixture
                    device.parameters = {}
                    device.footprint = 0
                    for param in fixture.parameters.values():
                        device.parameters[param.get("number")] = param.get("default")
                        param_type = param.get("type")
                        if param_type in ("HTP8", "LTP8"):
                            device.footprint += 1
                        elif param_type in ("HTP16", "LTP16"):
                            device.footprint += 2
                        else:
                            print("Device parameter type '{param_type}' not supported")
                            print("Supported types are : HTP8, LTP8, HTP16, LTP16")
                device.send_dmx()
            else:
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
            if f"{output}.{universe}" in self.channels[channel]:
                self.channels[channel][f"{output}.{universe}"].output = output
                self.channels[channel][f"{output}.{universe}"].universe = universe
                if (
                    self.channels[channel][f"{output}.{universe}"].fixture
                    is not fixture
                ):
                    self.channels[channel][f"{output}.{universe}"].fixture = fixture
                    self.channels[channel][f"{output}.{universe}"].parameters = {}
                    self.channels[channel][f"{output}.{universe}"].footprint = 0
                    for param in fixture.parameters.values():
                        self.channels[channel][f"{output}.{universe}"].parameters[
                            param.get("number")
                        ] = param.get("default")
                        param_type = param.get("type")
                        if param_type in ("HTP8", "LTP8"):
                            self.channels[channel][
                                f"{output}.{universe}"
                            ].footprint += 1
                        elif param_type in ("HTP16", "LTP16"):
                            self.channels[channel][
                                f"{output}.{universe}"
                            ].footprint += 2
                        else:
                            print("Device parameter type '{param_type}' not supported")
                            print("Supported types are : HTP8, LTP8, HTP16, LTP16")
            else:
                device = Device(channel, output, universe, fixture)
                self.channels[channel][f"{output}.{universe}"] = device
        else:
            # New patch, create device
            device = Device(channel, output, universe, fixture)
            self.channels[channel] = {}
            self.channels[channel][f"{output}.{universe}"] = device


class DMX:
    """DMX levels"""

    def __init__(self):
        self.levels = {}
        for universe in UNIVERSES:
            self.levels[universe] = [0] * 512

    def flush(self, universe):
        App().sender[universe].dmx_data = tuple(self.levels[universe])


class Console:
    """Application's heart"""

    def __init__(self):
        # Dimmer fixture at index 0
        self.fixtures = []
        dimmer = Fixture("Dimmer")
        dimmer.model_name = "Dimmer"
        self.fixtures.append(dimmer)

        self.patch = Patch()
        self.dmx = DMX()

        # Start sACN sender
        self.sender = sacn.sACNsender()
        self.sender.start()
        for universe in UNIVERSES:
            self.sender.activate_output(universe)
            self.sender[universe].multicast = True
