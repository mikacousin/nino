#!/usr/bin/env python3
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
"""Create devices templates found in Cobalt ASCII file"""
import argparse
import json
import os
import sys


class Template:
    def __init__(self, name):
        self.name = name
        self.manufacturer = ""
        self.model_name = ""
        self.mode_name = ""
        self.footprint = 0
        self.parameters = {}
        self.modes = []


class Parameter:
    def __init__(self, name, param_type):
        self.name = name
        self.type = param_type
        self.default = 0
        self.highlight = 0
        self.range = {}
        self.table = []


def make_index(index):
    for root, _dirs, files in os.walk("."):
        for name in files:
            if name not in ["groups.json", "index.json", "fixtures_ascii_to_json.py"]:
                file_name = os.path.join(root, name)
                with open(file_name, "r") as read_file:
                    d = json.load(read_file)
                index[file_name] = {
                    "manufacturer": d["manufacturer"],
                    "model_name": d["model_name"],
                    "modes": {},
                }
                for m in d["modes"]:
                    name = m["name"]
                    index[file_name]["modes"][name] = m["footprint"]

    with open("index.json", "w") as index_file:
        json.dump(index, index_file, indent=4, sort_keys=True)


templates = []
multi_parts = {}
index = {}

parser = argparse.ArgumentParser(
    description="Extract fixtures from ASCII file and generate index.json."
)
parser.add_argument("-f", "--file", type=str, help="ASCII Cue file to parse")
parser.add_argument(
    "-i", "--index", help="Generate index.json and exit (default)", action="store_true"
)
args = parser.parse_args()

if args.index or not args.file:
    make_index(index)
    sys.exit()

if not os.path.isfile(args.file):
    print(f"{args.file} not found.")
    sys.exit(1)

with open(args.file, "r", encoding="latin-1") as filename:
    data = filename.read().splitlines()

on_template = False
on_parameter = False

for line in data:
    if line[:10].upper() == "$TEMPLATE ":
        on_template = True
        name = line[10:]
        template = Template(name)
        templates.append(template)
        text_part = ""
    if on_template:
        if line[:0] == "!":
            on_template = False
        if line[:15].upper() == "$$MANUFACTURER ":
            template.manufacturer = line[15:]
        if line[:12].upper() == "$$MODELNAME ":
            template.model_name = line[12:]
        if line[:11].upper() == "$$MODENAME ":
            template.mode_name = line[11:]
        if line[:12].upper() == "$$FOOTPRINT ":
            template.footprint = int(line[12:])
        if line[:7].upper() == "$$DCID " and line[7:] in multi_parts:
            # This is another part of a template
            footprint = template.footprint
            template = multi_parts.get(line[7:])[0]
            template.footprint += footprint
            text_part = f" PART {multi_parts.get(line[7:])[1]}"
            del templates[-1]
        if line[:15].upper() == "$$TEMPLATEPART ":
            # template with several parts
            items = line[15:].split(" ")
            dcid = items[1]
            part = items[0]
            multi_parts[dcid] = (template, part)
        if line[:12].upper() == "$$PARAMETER ":
            items = line[12:].split(" ")
            if int(items[1]) == 0:
                param_type = "HTP8"
            elif int(items[1]) == 1:
                param_type = "HTP16"
            elif int(items[1]) == 2:
                param_type = "LTP8"
            elif int(items[1]) == 3:
                param_type = "LTP16"
            param_name = ""
            for item in items[5:]:
                param_name += item + " "
            param_name = param_name[:-1] + text_part
            parameter = Parameter(param_name, param_type)
            on_parameter = True
        if on_parameter:
            if line[:10].upper() == "$$DEFAULT ":
                parameter.default = int(line[10:])
            if line[:12].upper() == "$$HIGHLIGHT ":
                parameter.highlight = int(line[12:])
            if line[:8].upper() == "$$RANGE ":
                items = line[8:].split(" ")
                percent = int(items[2]) == 1
                parameter.range = {
                    "Minimum": int(items[0]),
                    "Maximum": int(items[1]),
                    "Percent": percent,
                }
            if line[:8].upper() == "$$TABLE ":
                items = line[8:].split(" ")
                start = int(items[0])
                stop = int(items[1])
                flags = int(items[2])
                range_name = ""
                for item in items[3:]:
                    range_name += item + " "
                range_name = range_name[:-1]
                parameter.table.append([start, stop, range_name, True])
            if line[:13].upper() == "$$RANGEGROUP ":
                pass
            if line == "":
                template.parameters[param_name] = parameter
                on_parameter = False

for template in templates:
    data = {
        "name": template.model_name,
        "manufacturer": template.manufacturer,
        "model_name": template.model_name,
        "parameters": {},
        "modes": [],
    }
    mode = {
        "name": template.mode_name,
        "footprint": template.footprint,
        "parameters": [],
    }
    for param, values in template.parameters.items():
        mode["parameters"].append(param)
        data["parameters"][param] = {
            "type": values.type,
            "default": values.default,
            "highlight": values.highlight,
        }
        if values.range:
            data["parameters"][param]["range"] = values.range
        elif values.table:
            data["parameters"][param]["table"] = values.table
    data["modes"].append(mode)

    path = f"{template.manufacturer}"
    if not os.path.isdir(path):
        os.makedirs(path)

    if template.model_name:
        file_name = f"{path}/{template.model_name} {template.mode_name}.json"
    else:
        file_name = f"{path}/{template.name}.json"

    if os.path.isfile(file_name):
        # If template already exist, merge new datas
        with open(file_name, "r") as read_file:
            old_data = json.load(read_file)
        # Merge dictionnaries
        if sys.version_info >= (3, 9):
            new_data = old_data | data
        elif sys.version_info >= (3, 5):
            new_data = {**old_data, **data}
        else:
            new_data = old_data.copy()
            new_data.update(data)
        with open(file_name, "w") as write_file:
            json.dump(new_data, write_file, indent=4, sort_keys=False)
    else:
        with open(file_name, "w") as write_file:
            json.dump(data, write_file, indent=4, sort_keys=False)

make_index(index)
