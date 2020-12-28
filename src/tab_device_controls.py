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
from gi.repository import Gdk, Gio, Gtk

import nino.shortcuts as shortcuts
from nino.defines import App
from nino.signals import gsignals
from nino.widgets_wheel import WheelWidget


class TabDeviceControls(Gtk.ScrolledWindow):
    """Device Controls Tab

    Attributes:
        window (Gtk.Window): Parent window
    """

    __gsignals__ = gsignals

    def __init__(self, window):
        Gtk.ScrolledWindow.__init__(self)
        self.window = window

        # Redirect channels selection signals to Live View
        self.connect("channel", App().tabs.get("live").channel)
        self.connect("thru", App().tabs.get("live").thru)
        self.connect("plus", App().tabs.get("live").plus)
        self.connect("minus", App().tabs.get("live").minus)

        self.big_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.big_box)
        # General Home parameters
        icon = Gio.ThemedIcon(name="go-home-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(image)
        button.connect("clicked", home)
        grid = Gtk.Grid()
        grid.add(button)
        self.big_box.add(grid)
        # Stack with groups parameters
        self.stacks = {
            "Intensity": {"stack": None, "parameters": {}},
            "Focus": {"stack": None, "parameters": {}},
            "Color": {"stack": None, "parameters": {}},
            "Beam": {"stack": None, "parameters": {}},
            "Effect": {"stack": None, "parameters": {}},
            "Control": {"stack": None, "parameters": {}},
        }
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        for param in self.stacks:
            self.stacks[param]["stack"] = Gtk.Grid()
            self.stacks[param]["stack"].set_column_spacing(10)
            self.stacks[param]["stack"].set_row_spacing(10)
            stack.add_titled(self.stacks.get(param).get("stack"), param, param)
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        self.big_box.pack_start(stack_switcher, False, False, 0)
        self.big_box.pack_start(stack, True, True, 0)

        self.populate()

    def populate(self):
        """Populate with device parameters"""
        # Delete children's Box container
        for param in self.stacks:
            children = self.stacks.get(param).get("stack").get_children()
            self.stacks[param]["parameters"] = {}
            for child in children:
                child.destroy()
        # Find selected devices
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                for device in channelwidget.devices:
                    for param, value in device.parameters.items():
                        self._create_parameter_widget(device, param, value)

    def _create_parameter_widget(self, device, param, value):
        """Create widgets

        Args:
            device (Device): Device
            param (str): Parameter
            value (int): Actual value
        """
        group = App().fixtures_param_grps.get(param)
        if param not in self.stacks[group]["parameters"]:
            self.stacks[group]["parameters"][param] = [device]
            if device.fixture.parameters.get(param).get("range"):
                box = RangeParameter(param, value)
                self.stacks[group]["stack"].add(box)
            elif device.fixture.parameters.get(param).get("table"):
                box = self.new_table_parameter(device.fixture, param, value)
                self.stacks[group]["stack"].add(box)
            else:
                print("No 'range' or 'table'")
        else:
            self.stacks[group]["parameters"][param].append(device)

    def new_table_parameter(self, fixture, param, value):
        """Widgets for table parameter

        Args:
            fixture (Fixture): Fixture used
            param (str): Parameter name
            value (int): Value

        Returns:
            Gtk.Box contained widgets
        """
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(Gtk.Label(param))
        # Home parameter
        button = Button(param)
        button.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon(name="go-home-symbolic"), Gtk.IconSize.BUTTON
            )
        )
        button.connect("clicked", parameter_to_home)
        grid = Gtk.Grid()
        grid.add(button)
        box.add(grid)
        spin = SpinButton(param)
        spin.set_numeric(True)
        spin.set_no_show_all(True)
        spin.connect("value-changed", self.spin_changed)
        spin.connect("focus-in-event", shortcuts.editable_focus)
        spin.connect("focus-out-event", shortcuts.editable_focus)
        # ListStore: text, param, mini, maxi, SpinButton, visible
        liststore = Gtk.ListStore(str, str, int, int, Gtk.SpinButton, bool)
        combo = Gtk.ComboBox.new_with_model(liststore)
        button.combo = combo
        box.add(combo)
        box.add(spin)
        for index, item in enumerate(fixture.parameters.get(param).get("table")):
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
        combo.connect("changed", on_combo_changed)
        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        return box

    def spin_changed(self, widget):
        """To adjust table value

        Args:
            widget (SpinButton): widget modified
        """
        group = App().fixtures_param_grps.get(widget.parameter)
        devices = self.stacks.get(group).get("parameters").get(widget.parameter)
        for device in devices:
            device.parameters[widget.parameter] = widget.get_value_as_int()
            device.send_dmx()

    def update_view(self):
        """Update view on parameters change"""
        for param in self.stacks:
            widgets = self.stacks.get(param).get("stack").get_children()
            for child in widgets:
                # Gtk.ComboBox, SpinButton, RangeParameter
                if isinstance(child, RangeParameter):
                    param = child.parameter
                    group = App().fixtures_param_grps.get(param)
                    devices = self.stacks.get(group).get("parameters").get(param)
                    value = devices[0].parameters.get(param)
                    child.set_value(value)
                if isinstance(child, SpinButton):
                    param = child.parameter
                    group = App().fixtures_param_grps.get(param)
                    devices = self.stacks.get(group).get("parameters").get(param)
                    value = devices[0].parameters.get(param)
                    child.set_value(value)
                elif isinstance(child, Gtk.ComboBox):
                    model = child.get_model()
                    param = model[0][1]
                    group = App().fixtures_param_grps.get(param)
                    devices = self.stacks.get(group).get("parameters").get(param)
                    value = devices[0].parameters.get(param)
                    for index, row in enumerate(model):
                        if row[2] <= value <= row[3]:
                            child.set_active(index)
                            break


def on_combo_changed(combo):
    """Change table value

    Args:
        combo (Gtk.ComboBox): widget modified
    """
    tree_iter = combo.get_active_iter()
    if tree_iter:
        model = combo.get_model()
        param = model[tree_iter][1]
        value = model[tree_iter][2]
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                if param in channelwidget.devices[0].parameters:
                    for device in channelwidget.devices:
                        device.parameters[param] = value
                        device.send_dmx()
        spin = model[tree_iter][4]
        spin.set_range(model[tree_iter][2], model[tree_iter][3])
        spin.set_value(value)
        spin.set_visible(model[tree_iter][5])


def home(_button):
    """All parameters to home"""
    selected = App().tabs.get("live").flowbox.get_selected_children()
    for flowboxchild in selected:
        children = flowboxchild.get_children()
        for channelwidget in children:
            for device in channelwidget.devices:
                device.home()


def parameter_to_home(button):
    """Sets parameter to home

    Args:
        button (Button): Home button clicked
    """
    selected = App().tabs.get("live").flowbox.get_selected_children()
    for flowboxchild in selected:
        children = flowboxchild.get_children()
        for channelwidget in children:
            if button.parameter in channelwidget.devices[0].parameters:
                for device in channelwidget.devices:
                    _set_home(device, button)


def _set_home(device, button):
    """Sets device parameter to home

    Args:
        device (Device): Device
        button (Button): Button clicked
    """
    value = device.fixture.parameters.get(button.parameter).get("default")
    device.parameters[button.parameter] = value
    device.send_dmx()
    model = button.combo.get_model()
    for index, row in enumerate(model):
        if row[2] <= value <= row[3]:
            button.combo.set_active(index)
            break


class Button(Gtk.Button):
    """Button widget

    Attributes:
        parameter (str): Device parameter controlled by the widget
    """

    def __init__(self, param):
        Gtk.Button.__init__(self)
        self.parameter = param
        self.combo = None


class SpinButton(Gtk.SpinButton):
    """SpinButton widget

    Attributes:
        parameter (str): Device parameter controlled by the widget
    """

    def __init__(self, param):
        Gtk.SpinButton.__init__(self)
        self.parameter = param


class RangeParameter(Gtk.Box):
    """Widgets for range parameter

    Attributes:
        parameter (str): Parameter name
        value (int): Value
    """

    def __init__(self, param, value):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.parameter = param
        self.value = value

        self.set_spacing(5)
        self.add(Gtk.Label(param))
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_spacing(5)
        icon = Gio.ThemedIcon(name="go-home-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.connect("clicked", self.parameter_to_home)
        button.add(image)
        box.add(button)
        self.label = Gtk.Label(value)
        box.add(self.label)
        self.add(box)
        button = Gtk.Button(label="Max")
        button.connect("clicked", self.set_value_to_max)
        self.add(button)
        wheel = WheelWidget(param)
        wheel.connect("moved", self.wheel_moved)
        self.add(wheel)
        button = Gtk.Button(label="Min")
        button.connect("clicked", self.set_value_to_min)
        self.add(button)

    def parameter_to_home(self, _button):
        """Sets parameter to home"""
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                if self.parameter in channelwidget.devices[0].parameters:
                    for device in channelwidget.devices:
                        value = device.fixture.parameters.get(self.parameter).get(
                            "default"
                        )
                        device.parameters[self.parameter] = value
                        param_type = device.fixture.parameters.get(self.parameter).get(
                            "type"
                        )
                        if param_type == "VIRTUAL" and self.parameter == "Intensity":
                            maxi = (
                                device.fixture.parameters.get(self.parameter)
                                .get("range")
                                .get("Maximum")
                            )
                            device.virtual_intensity = value / maxi
                        device.send_dmx()

    def set_value(self, value):
        """Sets the value and display it

        Args:
            value (int): Parameter's value
        """
        self.value = int(value)
        self.label.set_label(str(value))
        self.label.queue_draw()

    def set_value_to_max(self, _button):
        """Sets the value to its maximum"""
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                if self.parameter in channelwidget.devices[0].parameters:
                    for device in channelwidget.devices:
                        maxi = (
                            device.fixture.parameters.get(self.parameter)
                            .get("range")
                            .get("Maximum")
                        )
                        device.parameters[self.parameter] = maxi
                        param_type = device.fixture.parameters.get(self.parameter).get(
                            "type"
                        )
                        if param_type == "VIRTUAL" and self.parameter == "Intensity":
                            device.virtual_intensity = 1
                        device.send_dmx()

    def set_value_to_min(self, _button):
        """Sets the value to its minimum"""
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                if self.parameter in channelwidget.devices[0].parameters:
                    for device in channelwidget.devices:
                        mini = (
                            device.fixture.parameters.get(self.parameter)
                            .get("range")
                            .get("Minimum")
                        )
                        device.parameters[self.parameter] = mini
                        param_type = device.fixture.parameters.get(self.parameter).get(
                            "type"
                        )
                        if param_type == "VIRTUAL" and self.parameter == "Intensity":
                            maxi = (
                                device.fixture.parameters.get(self.parameter)
                                .get("range")
                                .get("Maximum")
                            )
                            device.virtual_intensity = mini / maxi
                        device.send_dmx()

    def wheel_moved(self, widget, direction, step, fine):
        """Change range value

        Args:
            widget (WheelWidget): wheel actioned
            direction (Gdk.ScrollDirection): Up or down
            step (int): increment or decrement step size
            fine (bool): True if actived
        """
        # List of list of devices
        selected = App().tabs.get("live").flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                if widget.parameter in channelwidget.devices[0].parameters:
                    for device in channelwidget.devices:
                        mini = (
                            device.fixture.parameters.get(widget.parameter)
                            .get("range")
                            .get("Minimum")
                        )
                        maxi = (
                            device.fixture.parameters.get(widget.parameter)
                            .get("range")
                            .get("Maximum")
                        )
                        param_type = device.fixture.parameters.get(
                            widget.parameter
                        ).get("type")
                        if not fine and param_type in ("HTP16", "LTP16"):
                            scale = 256
                        else:
                            scale = 1
                        level = device.parameters[widget.parameter]
                        self.value = level
                        if direction == Gdk.ScrollDirection.UP:
                            self.value = min(level + (step * scale), maxi)
                        elif direction == Gdk.ScrollDirection.DOWN:
                            self.value = max(level - (step * scale), mini)
                        device.parameters[widget.parameter] = self.value
                        if param_type == "VIRTUAL" and widget.parameter == "Intensity":
                            device.virtual_intensity = self.value / maxi
                        device.send_dmx()
