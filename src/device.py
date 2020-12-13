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
from nino.defines import App


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
        list_param = self.fixture.mode.get("parameters")
        for name, param in self.fixture.parameters.items():
            if name in list_param:
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
        """Send device parameters"""
        if not self.output:
            return
        for name, value in self.parameters.items():
            param_type = self.fixture.parameters[name].get("type")
            offset = self.fixture.parameters[name].get("offset")
            if param_type in ("HTP8", "LTP8"):
                out = self.output + offset.get("High Byte") - 1
                if value > 255:
                    val = (value >> 8) & 0xFF
                else:
                    val = value
                App().dmx.levels[self.universe][out] = val
            elif param_type in ("HTP16", "LTP16"):
                out = self.output + offset.get("High Byte") - 1
                val = (value >> 8) & 0xFF
                out2 = self.output + offset.get("Low Byte") - 1
                val2 = value & 0xFF
                App().dmx.levels[self.universe][out] = val
                App().dmx.levels[self.universe][out2] = val2
        App().dmx.flush(self.universe)
