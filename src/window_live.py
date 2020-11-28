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
from gi.repository import Gio, Gtk

from nino.tab_live import TabLive


class LiveWindow(Gtk.ApplicationWindow):
    """Niño's live window.

    Attributes:
        app (Nino): Application
    """

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, title="Niño", application=app)

        self.set_default_size(1440, 900)

        header = Gtk.HeaderBar(title="Niño")
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

        self.notebook = Gtk.Notebook()
        self.notebook.append_page(TabLive(), Gtk.Label("Live"))
        self.add(self.notebook)

        self.connect("destroy", app._exit, None)
