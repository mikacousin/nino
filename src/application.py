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
from gettext import gettext as _
from gi.repository import Gdk, Gio, GLib, Gtk

import nino.shortcuts as shortcuts
from nino.console import Console
from nino.settings import Settings, TabSettings
from nino.tab_device_controls import TabDeviceControls
from nino.tab_patch import TabPatch
from nino.window_live import LiveWindow
from nino.window_playback import PlaybackWindow


class Nino(Gtk.Application, Console):
    """niño is a Gtk application"""

    def __init__(self):
        Console.__init__(self)
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
        # About window
        self.about = None
        # Application settings
        self.settings = Settings.new()

        self.init_notebooks()

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
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", True
        )
        # Create 2 windows
        self.create_main_windows()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        shortcuts.setup_shortcuts()

    def create_main_windows(self):
        """Create and activate main window."""
        nb_monitors = Gdk.Display.get_default().get_n_monitors()
        if not self.live:
            self.live = LiveWindow(self)
        if not self.playback:
            self.playback = PlaybackWindow(self)
        if nb_monitors > 1:
            # With 2 monitors, open each window on different monitors and maximize it
            display = Gdk.Display.get_default()
            monitor = display.get_monitor(0)
            monitor_geometry = monitor.get_geometry()
            self.live.move(monitor_geometry.x, monitor_geometry.y)
            monitor = display.get_monitor(1)
            monitor_geometry = monitor.get_geometry()
            self.playback.move(monitor_geometry.x, monitor_geometry.y)
            self.live.maximize()
            self.playback.maximize()
        self.live.show_all()
        self.playback.show_all()

    def init_notebooks(self):
        """Notebooks initialization"""
        self.tabs = {
            "device_controls": None,
            "live": None,
            "patch": None,
            "settings": None,
        }

    def setup_app_menu(self):
        """Setup application menu.

        Returns:
            Gio.Menu: Application menu for main popover
        """
        builder = Gtk.Builder()
        builder.add_from_resource("/com/github/mikacousin/nino/menu.ui")
        menu = builder.get_object("app-menu")
        actions = {
            "device_controls": ("_device_controls", None),
            "shortcuts": ("_shortcuts", None),
            "about": ("_about", None),
            "settings": ("_settings", None),
            "quit": ("_exit", None),
            "undo": ("_undo", None),
            "redo": ("_redo", None),
            "patch": ("_patch", None),
            "close_tab": ("_close_tab", None),
            "clear": ("_clear", None),
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
            "dot": ("_dot", None),
            "channel": ("_channel", None),
            "thru": ("_thru", None),
            "plus": ("_plus", None),
            "minus": ("_minus", None),
            "at_level": ("_at_level", None),
            "output": ("_output", None),
            "offset": ("_offset", None),
            "insert": ("_insert", None),
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

    def _patch(self, _action, _parameter):
        active = self.get_active_window()
        if self.tabs["patch"] is None:
            self.tabs["patch"] = TabPatch(active)
            active.notebook.append_page(self.tabs["patch"], Gtk.Label("Patch"))
            active.notebook.show_all()
            active.notebook.set_current_page(-1)
        else:
            win = self.tabs["patch"].window
            page = win.notebook.page_num(self.tabs["patch"])
            win.notebook.set_current_page(page)

    def _device_controls(self, _action, _parameter):
        active = self.get_active_window()
        if self.tabs["device_controls"] is None:
            self.tabs["device_controls"] = TabDeviceControls(active)
            active.notebook.append_page(
                self.tabs["device_controls"], Gtk.Label("Device Controls")
            )
            active.notebook.show_all()
            active.notebook.set_current_page(-1)
        else:
            win = self.tabs["device_controls"].window
            page = win.notebook.page_num(self.tabs["device_controls"])
            win.notebook.set_current_page(page)

    def _settings(self, _action, _parameter):
        active = self.get_active_window()
        if self.tabs["settings"] is None:
            self.tabs["settings"] = TabSettings(active)
            active.notebook.append_page(
                self.tabs["settings"], Gtk.Label(_("Preferences"))
            )
            active.notebook.show_all()
            active.notebook.set_current_page(-1)
        else:
            win = self.tabs["settings"].window
            page = win.notebook.page_num(self.tabs["settings"])
            win.notebook.set_current_page(page)

    def _close_tab(self, _action, _parameter):
        active = self.get_active_window()
        page = active.notebook.get_current_page()
        if page:
            widget = active.notebook.get_nth_page(page)
            active.notebook.remove_page(page)
            for name, tab in self.tabs.items():
                if widget == tab:
                    self.tabs[name] = None

    def _shortcuts(self, _action, _parameter):
        builder = Gtk.Builder()
        builder.add_from_resource("/com/github/mikacousin/nino/shortcuts.ui")
        shortcut = builder.get_object("shortcuts")
        window = self.get_active_window()
        shortcut.set_transient_for(window)
        shortcut.show()

    def _about(self, _action, _parameter):
        if not self.about:
            builder = Gtk.Builder()
            builder.add_from_resource("/com/github/mikacousin/nino/about.ui")
            self.about = builder.get_object("about_dialog")
            window = self.get_active_window()
            self.about.set_transient_for(window)
            self.about.connect("response", self._about_response)
            self.about.show()
        else:
            self.about.present()

    def _about_response(self, dialog, _response):
        """Destroy about dialog when closed

        Args:
            dialog: Gtk.Dialog
            _response: int
        """
        dialog.destroy()
        self.about = None

    def _exit(self, _action, _parameter):
        self.console_exit()
        self.quit()

    def _undo(self, _action, _parameter):
        if self.undo_manager.can_undo():
            self.undo_manager.undo()

    def _redo(self, _action, _parameter):
        if self.undo_manager.can_redo():
            self.undo_manager.redo()

    def _clear(self, _action, _parameter):
        self.statusbar_remove_all()

    def _number(self, _action, param):
        self.keystring += str(param)
        self.statusbar_push()

    def _dot(self, _action, _parameter):
        self.keystring += "."
        self.statusbar_push()

    def _channel(self, _action, _parameter):
        self.send("channel")

    def _thru(self, _action, _parameter):
        self.send("thru")

    def _plus(self, _action, _parameter):
        self.send("plus")

    def _minus(self, _action, _parameter):
        self.send("minus")

    def _at_level(self, _action, _parameter):
        self.send("at_level")

    def _output(self, _action, _parameter):
        self.send("output")

    def _insert(self, _action, _parameter):
        self.send("insert")

    def _offset(self, _action, _parameter):
        self.send("offset")

    def send(self, signal):
        """Send signal to the right place

        Args:
            signal (str): signal to send
        """
        active = self.get_active_window()
        if active in [self.live, self.playback]:
            page = active.notebook.get_current_page()
            child = active.notebook.get_nth_page(page)
            child.emit(signal)
        else:
            print("Another window")

    def statusbar_push(self):
        """Push keystring to StatusBars"""
        self.live.statusbar.push(self.playback.context_id, self.keystring)
        self.playback.statusbar.push(self.playback.context_id, self.keystring)

    def statusbar_remove_all(self):
        """Empty StatusBars"""
        self.keystring = ""
        self.live.statusbar.remove_all(self.playback.context_id)
        self.playback.statusbar.remove_all(self.playback.context_id)
