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
from gettext import gettext as _
from gi.repository import Gio, Gtk

from nino.defines import App


class Settings(Gio.Settings):
    """niño settings"""

    def __init__(self):
        Gio.Settings.__init__(self)

    # pylint: disable=no-method-argument,no-self-use
    def new():
        """New instance of Gio.Settings.

        Returns:
            Gio.Settings
        """
        settings = Gio.Settings.new("com.github.mikacousin.nino")
        settings.__class__ = Settings
        return settings

    @property
    def percent_mode(self):
        """Get percent mode.

        Returns:
            True if percent mode is on, False if off
        """
        return self.get_boolean("percent")

    @percent_mode.setter
    def percent_mode(self, mode):
        """Set percent mode.

        Args:
            mode (bool): True = on, False = off
        """
        self.set_boolean("percent", mode)


class TabSettings(Gtk.ScrolledWindow):
    """Settings Dialog

    Attributes:
        window (Gtk.Window): Parent window
    """

    def __init__(self, window):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window = window

        label = Gtk.Label(_("Percent mode"))
        switch = Gtk.Switch()
        switch.connect("notify::active", _percent_mode)
        switch.set_active(App().settings.percent_mode)
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.add(label)
        grid.add(switch)
        self.add(grid)


def _percent_mode(widget, _gparam):
    """Change percent mode

    Args:
        widget (Gtk.Switch): widget actionned
    """
    App().settings.percent_mode = widget.get_active()
    # Update Live view
    App().tabs.get("live").flowbox.invalidate_filter()
