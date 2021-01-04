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
                "range": {"Minimum": 0, "Maximum": 255, "Percent": True},
            }
        }
        self.mode = {"name": "", "parameters": ["Intensity"]}

    def get_footprint(self):
        """Return footprint

        Returns:
            footprint (int)
        """
        footprint = 0
        list_param = self.mode.get("parameters")
        for name, param in self.parameters.items():
            if name in list_param:
                param_type = param.get("type")
                if param_type in ("HTP8", "LTP8"):
                    footprint += 1
                elif param_type in ("HTP16", "LTP16"):
                    footprint += 2
                else:
                    print("Device parameter type '{param_type}' not supported")
                    print("Supported types are : HTP8, LTP8, HTP16, LTP16")
        return footprint
