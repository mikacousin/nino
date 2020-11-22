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
from gi.repository import Gdk, Gio, GLib, Gtk

from nino.window_live import LiveWindow
from nino.window_playback import PlaybackWindow


class Nino(Gtk.Application):
    """Niño is a Gtk application

    Attributes:
        gui (MainWindow): Application's main window
    """

    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id="com.github.mikacousin.nino",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        # Main Windows
        self.live = None
        self.playback = None
        # String for command
        self.keystring = ""

    def do_activate(self):
        css_provider_file = Gio.File.new_for_uri(
            "resource://com/github/mikacousin/nino/nino.css"
        )
        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(css_provider_file)
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        # Use dark theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)
        self.create_main_windows()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.setup_shortcuts()

    def create_main_windows(self):
        """Create and activate main window."""
        nb_monitors = Gdk.Display.get_default().get_n_monitors()
        if not self.live:
            self.live = LiveWindow(self)
            self.live.move(0, 0)
        if not self.playback:
            self.playback = PlaybackWindow(self)
            if nb_monitors > 1:
                display = Gdk.Display.get_default()
                monitor = display.get_monitor(1)
                monitor_geometry = monitor.get_geometry()
                self.playback.move(monitor_geometry.x, monitor_geometry.y)
        self.live.show_all()
        self.playback.show_all()

    def setup_app_menu(self):
        """Setup application menu.

        Returns:
            Gio.Menu: Application menu for main popover
        """
        builder = Gtk.Builder()
        builder.add_from_resource("/com/github/mikacousin/nino/menu.ui")
        menu = builder.get_object("app-menu")
        actions = {
            "quit": ("_exit", None),
            "one": ("_number", "i"),
            "two": ("_number", "i"),
            "three": ("_number", "i"),
            "four": ("_number", "i"),
            "five": ("_number", "i"),
            "six": ("_number", "i"),
            "seven": ("_number", "i"),
            "eight": ("_number", "i"),
            "nine": ("_number", "i"),
            "zero": ("_number", "i"),
            "channel": ("_channel", None),
            "output": ("_output", None),
        }
        for name, func in actions.items():
            function = getattr(self, func[0], None)
            if func[1]:
                action = Gio.SimpleAction.new(name, GLib.VariantType(func[1]))
            else:
                action = Gio.SimpleAction.new(name, None)
            action.connect("activate", function)
            self.add_action(action)
        return menu

    def setup_shortcuts(self):
        """Application shortcuts"""
        self.set_accels_for_action("app.quit", ["<Control>q"])
        self.set_accels_for_action("app.one(1)", ["1"])
        self.set_accels_for_action("app.two(2)", ["2"])
        self.set_accels_for_action("app.three(3)", ["3"])
        self.set_accels_for_action("app.four(4)", ["4"])
        self.set_accels_for_action("app.five(5)", ["5"])
        self.set_accels_for_action("app.six(6)", ["6"])
        self.set_accels_for_action("app.seven(7)", ["7"])
        self.set_accels_for_action("app.eight(8)", ["8"])
        self.set_accels_for_action("app.nine(9)", ["9"])
        self.set_accels_for_action("app.zero(0)", ["0"])
        self.set_accels_for_action("app.channel", ["c"])
        self.set_accels_for_action("app.output", ["o"])

    def _exit(self, _action, _parameter):
        self.quit()

    def _number(self, _action, param):
        self.keystring += str(param)
        self.playback.statusbar.push(self.playback.context_id, self.keystring)

    def _channel(self, _action, _parameter):
        self.send("channel")

    def _output(self, _action, _parameter):
        self.send("output")

    def send(self, signal):
        """Send signal to the right place

        Args:
            signal (str): signal to send
        """
        active = self.get_active_window()
        if active == self.live:
            page = active.notebook.get_current_page()
            child = active.notebook.get_nth_page(page)
            child.emit(signal)
        elif active == self.playback:
            print("PLayback window")
        else:
            print("Another window")
