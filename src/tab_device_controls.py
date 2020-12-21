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
from gi.repository import Gio, Gtk

import nino.shortcuts as shortcuts
from nino.defines import App
from nino.signals import gsignals


class TabDeviceControls(Gtk.ScrolledWindow):
    """Device Controls Tab

    Attributes:
        window (Gtk.Window): Parent window
    """

    __gsignals__ = gsignals

    def __init__(self, window):
        Gtk.ScrolledWindow.__init__(self)
        self.window = window

        self.big_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.big_box)

        self.populate()

    def populate(self):
        """Populate with device parameters"""
        # Delete children's Box container
        children = self.big_box.get_children()
        for child in children:
            child.destroy()
        # General Home parameters
        icon = Gio.ThemedIcon(name="go-home-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(image)
        button.connect("clicked", self.home)
        self.big_box.add(button)
        # Find selected devices with same model
        self.devices = []
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                name = channelwidget.device.fixture.name
                if not self.devices:
                    self.devices.append(channelwidget.device)
                elif self.devices[-1].fixture.name == name:
                    self.devices.append(channelwidget.device)
        if self.devices:
            for param, value in self.devices[0].parameters.items():
                if self.devices[0].fixture.parameters.get(param).get("range"):
                    box = self.new_range_parameter(param, value)
                    self.big_box.add(box)
                elif self.devices[0].fixture.parameters.get(param).get("table"):
                    box = self.new_table_parameter(param, value)
                    self.big_box.add(box)
                else:
                    print("No 'range' or 'table'")

    def new_range_parameter(self, param, value):
        """Widgets for range parameter

        Args:
            param (str): Parameter name
            value (int): Value

        Returns:
            Gtk.Box contained widgets
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mini = self.devices[0].fixture.parameters.get(param).get("range").get("Minimum")
        maxi = self.devices[0].fixture.parameters.get(param).get("range").get("Maximum")
        adj = Gtk.Adjustment(value=value, lower=mini, upper=maxi)
        scale = Scale(param, orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        scale.set_digits(0)
        scale.connect("value-changed", self.scale_moved)
        box.pack_start(Gtk.Label(param), False, False, 0)
        box.pack_start(scale, True, True, 0)
        return box

    def new_table_parameter(self, param, value):
        """Widgets for table parameter

        Args:
            param (str): Parameter name
            value (int): Value

        Returns:
            Gtk.Box contained widgets
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add(Gtk.Label(param))
        table = self.devices[0].fixture.parameters.get(param).get("table")
        spin = SpinButton(param)
        spin.set_numeric(True)
        spin.set_no_show_all(True)
        spin.connect("value-changed", self.spin_changed)
        spin.connect("focus-in-event", shortcuts.editable_focus)
        spin.connect("focus-out-event", shortcuts.editable_focus)
        # ListStore: text, param, mini, maxi, SpinButton, visible
        liststore = Gtk.ListStore(str, str, int, int, Gtk.SpinButton, bool)
        combo = Gtk.ComboBox.new_with_model(liststore)
        box.add(combo)
        box.add(spin)
        for index, item in enumerate(table):
            try:
                spin_visible = item[3]
            except IndexError:
                spin_visible = True
            liststore.append([item[2], param, item[0], item[1], spin, spin_visible])
            if item[0] <= value <= item[1]:
                combo.set_active(index)
                adj = Gtk.Adjustment(
                    lower=item[0],
                    upper=item[1],
                    step_increment=1,
                    page_increment=10,
                )
                spin.set_adjustment(adj)
                spin.set_value(value)
                spin.set_visible(spin_visible)
        combo.set_wrap_width(3)
        combo.connect("changed", self.on_combo_changed)
        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        return box

    def spin_changed(self, widget):
        """To adjust table value

        Args:
            widget (SpinButton): widget modified
        """
        for device in self.devices:
            device.parameters[widget.parameter] = widget.get_value_as_int()
            device.send_dmx()

    def on_combo_changed(self, combo):
        """Change table value

        Args:
            combo (Gtk.ComboBox): widget modified
        """
        tree_iter = combo.get_active_iter()
        if tree_iter:
            model = combo.get_model()
            param = model[tree_iter][1]
            value = model[tree_iter][2]
            for device in self.devices:
                device.parameters[param] = value
                device.send_dmx()
            spin = model[tree_iter][4]
            spin.set_range(model[tree_iter][2], model[tree_iter][3])
            spin.set_value(value)
            spin.set_visible(model[tree_iter][5])

    def scale_moved(self, widget):
        """Change range value

        Args:
            widget (Scale): widget modified
        """
        for device in self.devices:
            device.parameters[widget.parameter] = int(widget.get_value())
            device.send_dmx()

    def home(self, _button):
        """All parameters to home"""
        for device in self.devices:
            device.home()

    def update_view(self):
        """Update view on parameters change"""
        widgets = self.big_box.get_children()
        for widget in widgets:
            children = widget.get_children()
            for child in children:
                # Gtk.ComboBox, SpinButton, Scale
                if isinstance(child, Scale):
                    param = child.parameter
                    value = self.devices[0].parameters.get(param)
                    child.set_value(value)
                elif isinstance(child, SpinButton):
                    param = child.parameter
                    value = self.devices[0].parameters.get(param)
                    child.set_value(value)
                elif isinstance(child, Gtk.ComboBox):
                    model = child.get_model()
                    param = model[0][1]
                    value = self.devices[0].parameters.get(param)
                    for index, row in enumerate(model):
                        if row[2] <= value <= row[3]:
                            child.set_active(index)
                            break


class Scale(Gtk.Scale):
    """Scale widget

    Attributes:
        parameter (str): Device parameter controlled by the widget
    """

    def __init__(self, param, orientation=None, adjustment=None):
        Gtk.Scale.__init__(self, orientation=orientation, adjustment=adjustment)
        self.parameter = param


class SpinButton(Gtk.SpinButton):
    """SpinButton widget

    Attributes:
        parameter (str): Device parameter controlled by the widget
    """

    def __init__(self, param):
        Gtk.SpinButton.__init__(self)
        self.parameter = param
