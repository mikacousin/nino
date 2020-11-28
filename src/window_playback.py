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
from gi.repository import Gtk


class PlaybackWindow(Gtk.ApplicationWindow):
    """Niño's main playback window.

    Attributes:
        app (Nino): Application
    """

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, title="Niño", application=app)
        self.app = app

        self.set_default_size(1440, 900)

        vbox = Gtk.VBox()

        self.notebook = Gtk.Notebook()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        label = Gtk.Label("Main Playback")
        scrolled.add(label)
        self.notebook.append_page(scrolled, Gtk.Label("Playback"))
        vbox.pack_start(self.notebook, True, True, 0)

        self.statusbar = Gtk.Statusbar()
        self.context_id = self.statusbar.get_context_id("keypress")
        vbox.pack_end(self.statusbar, False, False, 0)

        self.add(vbox)

        self.connect("destroy", app._exit, None)
