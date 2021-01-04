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
from gi.repository import Gio, Gtk

from nino.tab_live import TabLive


class LiveWindow(Gtk.ApplicationWindow):
    """niño's live window.

    Attributes:
        app (Nino): Application
    """

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, title="niño", application=app)

        self.set_default_size(1440, 900)

        header = Gtk.HeaderBar(title="Live")
        header.set_show_close_button(True)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button = Gtk.MenuButton()
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        box.add(button)
        popover = Gtk.Popover.new_from_model(button, app.setup_app_menu())
        button.set_popover(popover)
        header.pack_end(box)
        self.set_titlebar(header)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.notebook = Gtk.Notebook()
        app.tabs["live"] = TabLive()
        self.notebook.append_page(app.tabs.get("live"), Gtk.Label("Live"))
        vbox.pack_start(self.notebook, True, True, 0)

        self.statusbar = Gtk.Statusbar()
        self.context_id = self.statusbar.get_context_id("keypress")
        vbox.pack_end(self.statusbar, False, False, 0)

        self.add(vbox)

        self.connect("destroy", app._exit, None)
