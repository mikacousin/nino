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
from gi.repository import Gtk

from nino.defines import App, MAX_CHANNELS
from nino.signals import gsignals
from nino.widgets_channel import ChannelWidget


class TabLive(Gtk.ScrolledWindow):
    """Live view"""

    __gsignals__ = gsignals

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.last_chan = None
        # Connect signals
        self.connect("channel", self.channel)
        self.connect("thru", self.thru)
        self.connect("plus", self.plus)
        self.connect("minus", self.minus)
        self.connect("at_level", self.at_level)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(MAX_CHANNELS)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.flowbox.set_filter_func(filter_channels, None)
        self.channels = []
        for channel in range(MAX_CHANNELS):
            self.channels.append(ChannelWidget(channel + 1))
            self.flowbox.add(self.channels[channel])

        self.add(self.flowbox)

    def channel(self, _widget):
        """channel signal received"""
        if not App().keystring or not App().keystring.isdigit():
            App().statusbar_remove_all()
            return
        self.flowbox.unselect_all()
        if App().keystring != "0":
            channel = int(App().keystring) - 1
            if 0 <= channel < MAX_CHANNELS and (channel + 1) in App().patch.channels:
                child = self.flowbox.get_child_at_index(channel)
                self.flowbox.select_child(child)
                child.grab_focus()
                self.last_chan = channel
        App().statusbar_remove_all()

    def thru(self, _widget):
        """Thru signal received"""
        if not App().keystring or not App().keystring.isdigit():
            App().statusbar_remove_all()
            return
        select = self.flowbox.get_selected_children()
        if len(select) == 1:
            flowboxchild = select[0]
            channelwidget = flowboxchild.get_children()[0]
            self.last_chan = channelwidget.channel
        if self.last_chan:
            channel = int(App().keystring) - 1
            if channel > self.last_chan:
                for chan in range(self.last_chan, channel + 1):
                    child = self.flowbox.get_child_at_index(chan)
                    self.flowbox.select_child(child)
            else:
                for chan in range(channel, self.last_chan):
                    child = self.flowbox.get_child_at_index(chan)
                    self.flowbox.select_child(child)
            child = self.flowbox.get_child_at_index(channel)
            child.grab_focus()
            self.last_chan = channel
        App().statusbar_remove_all()

    def plus(self, _widget):
        """+ signal"""
        if not App().keystring or not App().keystring.isdigit():
            App().statusbar_remove_all()
            return
        channel = int(App().keystring) - 1
        if 0 <= channel < MAX_CHANNELS and (channel + 1) in App().patch.channels:
            child = self.flowbox.get_child_at_index(channel)
            self.flowbox.select_child(child)
            child.grab_focus()
            self.last_chan = channel
        App().statusbar_remove_all()

    def minus(self, _widget):
        """- signal"""
        if not App().keystring or not App().keystring.isdigit():
            App().statusbar_remove_all()
            return
        channel = int(App().keystring) - 1
        if 0 <= channel < MAX_CHANNELS and (channel + 1) in App().patch.channels:
            child = self.flowbox.get_child_at_index(channel)
            self.flowbox.unselect_child(child)
            child.grab_focus()
            self.last_chan = channel
        App().statusbar_remove_all()

    def at_level(self, _widget):
        """At level signal"""
        if not App().keystring or not App().keystring.isdigit():
            App().statusbar_remove_all()
            return
        level = int(App().keystring)
        selected = self.flowbox.get_selected_children()
        for flowboxchild in selected:
            children = flowboxchild.get_children()
            for channelwidget in children:
                mini = (
                    channelwidget.device.fixture.parameters.get("Intensity")
                    .get("range")
                    .get("Minimum")
                )
                maxi = (
                    channelwidget.device.fixture.parameters.get("Intensity")
                    .get("range")
                    .get("Maximum")
                )
                if level < mini:
                    level = mini
                elif level > maxi:
                    level = maxi
                channelwidget.device.parameters["Intensity"] = level
                channelwidget.device.send_dmx()
        App().statusbar_remove_all()


def filter_channels(child, _user_data):
    """Display only patched channels

    Args:
        child (Gtk.FlowBoxChild): widget filtered

    Returns:
        (bool)
    """
    channel = child.get_index() + 1
    devices = App().patch.channels.get(channel)
    if devices:
        for device in devices.values():
            if device.output:
                return True
    return False
