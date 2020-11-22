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
        self.label = Gtk.Label("Live view")
        self.add(self.label)

    def channel(self, _widget):
        """channel signal received"""
        print(f"{self.label.get_label()}: channel signal")
