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
from gi.repository import GObject, Gtk

from nino.defines import App, MAX_CHANNELS
from nino.widgets_channel import ChannelWidget


class TabLive(Gtk.ScrolledWindow):
    """Live view"""

    __gsignals__ = {
        "one": (GObject.SignalFlags.ACTION, None, ()),
        "channel": (GObject.SignalFlags.ACTION, None, ()),
    }

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        # Connect signals
        self.connect("channel", self.channel)

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
        print("channel signal")


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