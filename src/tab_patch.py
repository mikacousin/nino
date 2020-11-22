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
import json
import os

from gi.repository import GObject, Gtk

from nino.defines import App, MAX_CHANNELS, UNIVERSES
from nino.paths import get_fixtures_dir
from nino.widgets_output import OutputWidget

# TODO:
# - Clear patch when change fixture
# - If no fixture, patch dimmer


class FixturesLibrary(Gtk.VBox):
    """Fixtures library

    Attributes:
        show_fixtures (Fixtures): Fixtures in the show
    """

    def __init__(self, fixtures):
        Gtk.VBox.__init__(self)

        self.show_fixtures = fixtures

        # TODO: Just for tests
        # Load fixtures index
        path = get_fixtures_dir()
        with open(os.path.join(path, "index.json"), "r") as index_file:
            data = json.load(index_file)
        manufacturers = {}
        for files in data.values():
            manu = files.get("manufacturer")
            manufacturers[manu] = {}
        for files in data.values():
            manu = files.get("manufacturer")
            model = files.get("model_name")
            manufacturers[manu][model] = []
        for files in data.values():
            manu = files.get("manufacturer")
            model = files.get("model_name")
            mode = files.get("mode")
            manufacturers[manu][model].append(mode)

        # Fixtures treestore
        self.fixtures = Gtk.TreeStore(bool, str)
        for manu, models in manufacturers.items():
            if manu not in ("Internal", "Scrollers"):
                piter = self.fixtures.append(None, [True, manu])
                for model, modes in models.items():
                    piter2 = self.fixtures.append(piter, [True, model])
                    for mode in modes:
                        self.fixtures.append(piter2, [True, mode])
        # Search fixtures
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Enter fixture name")
        self.search_entry.connect("changed", self.refresh_results)
        self.search_entry.connect("focus-in-event", focus)
        self.search_entry.connect("focus-out-event", focus)
        self.filter = self.fixtures.filter_new()
        self.filter.set_visible_column(0)
        self.pack_start(self.search_entry, False, False, 0)
        # Fixtures treeview
        self.view = Gtk.TreeView(model=self.filter)
        self.view.connect("row-activated", self.fixtures_activated)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Fixtures", renderer, text=1)
        self.view.append_column(column)
        self.pack_end(self.view, True, True, 0)

    def refresh_results(self, _widget):
        """Update fixtures treeview when enter search string"""
        query = self.search_entry.get_text().lower()
        if not query:
            self.fixtures.foreach(self.reset_row, True)
            self.view.collapse_all()
        else:
            self.fixtures.foreach(self.reset_row, False)
            self.fixtures.foreach(self.show_matches, query)
            self.view.expand_all()
        self.filter.refilter()

    def reset_row(self, _model, _path, iterr, visible):
        """Reset row

        Args:
            iterr (Gtk.TreeIter): iter
            visible (bool): Mark row visible or not
        """
        self.fixtures.set_value(iterr, 0, visible)

    def show_matches(self, model, _path, iterr, query):
        """Test if row match search string

        Args:
            model (Gtk.TreeModel): Model
            iterr (Gtk.TreeIter): iter
            query (str): Search string
        """
        text = model.get_value(iterr, 1).lower()
        if query in text:
            self.make_path_visible(model, iterr)
            self.make_subtree_visible(model, iterr)

    def make_subtree_visible(self, model, iterr):
        """Display subtree of matching branch

        Args:
            model (Gtk.TreeModel): Model
            iterr (Gtk.TreeIter): iter
        """
        for i in range(model.iter_n_children(iterr)):
            subtree = model.iter_nth_child(iterr, i)
            if model.get_value(subtree, 0):
                continue
            self.fixtures.set_value(subtree, 0, True)
            self.make_subtree_visible(model, subtree)

    def make_path_visible(self, model, iterr):
        """Make branch visible

        Args:
            model (Gtk.TreeModel): Model
            iterr (Gtk.TreeIter): iter
        """
        while iterr:
            self.fixtures.set_value(iterr, 0, True)
            iterr = model.iter_parent(iterr)

    def fixtures_activated(self, treeview, path, _column):
        """Double-click, Enter, Space, ... on treeview

        Args:
            treeview (Gtk.TreeView): treeview
            path (Gtk.TreePath): path
        """
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)
        depth = path.get_depth()
        if depth == 3:
            # A mode is activate, add fixture to the show
            model = treeview.get_model()
            fixture_mode = model[path][1]
            path.up()
            fixture_model = model[path][1]
            label = f"{fixture_model} {fixture_mode}"
            # If fixture is already in show, doesn't add it
            found = False
            for child in self.show_fixtures.flowbox.get_children():
                if child.get_children()[0].get_label() == label:
                    found = True
                    break
            if not found:
                button = Gtk.Button.new_with_label(label)
                button.connect("clicked", self.show_fixtures.clicked)
                self.show_fixtures.flowbox.add(button)
                self.show_fixtures.flowbox.show_all()


class Fixtures(Gtk.ScrolledWindow):
    """Fixtures in the show

    Attributes:
        channels (Gtk.TreeView): Channels treeview
    """

    def __init__(self, channels):
        Gtk.ScrolledWindow.__init__(self)

        # TODO: Just for tests
        # Fixtures
        fixtures = ["Dimmer"]

        self.channels = channels

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        for fixture in fixtures:
            button = Gtk.Button.new_with_label(fixture)
            button.connect("clicked", self.clicked)
            self.flowbox.add(button)
        self.add(self.flowbox)

    def clicked(self, button):
        """Button clicked, set channel type

        Args:
            button (Gtk.Button): button clicked
        """
        label = button.get_label()
        model, selected_channels = self.channels.get_selection().get_selected_rows()
        for path in selected_channels:
            model[path][2] = label


class TabPatch(Gtk.Box):
    """Tab Patch

    Attributes:
        keystring (str): String of command
    """

    __gsignals__ = {
        "channel": (GObject.SignalFlags.ACTION, None, ()),
        "output": (GObject.SignalFlags.ACTION, None, ()),
    }

    def __init__(self, window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # Connect signals
        self.connect("channel", self.channel)
        self.connect("output", self.output)

        # Paned container
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        window_width = window.get_size()[0]
        paned.set_position(window_width / 2)
        self.add(paned)

        # Channels list and Templates
        liststore = Gtk.ListStore(int, str, str)
        for chan in range(1, MAX_CHANNELS + 1):
            liststore.append([chan, "", ""])
        self.treeview = Gtk.TreeView(model=liststore)
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.treeview.set_activate_on_single_click(True)
        for i, column_title in enumerate(["Chan", "Address", "Type"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
        scrollable = Gtk.ScrolledWindow()
        scrollable.set_vexpand(True)
        scrollable.set_hexpand(True)
        scrollable.add(self.treeview)
        paned2 = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        window_height = window.get_size()[1]
        paned2.set_position((window_height / 8) * 5)
        paned2.pack1(scrollable, resize=True, shrink=False)
        fixtures = Fixtures(self.treeview)
        paned2.pack2(fixtures, resize=True, shrink=False)
        paned.pack1(paned2, resize=True, shrink=False)

        # sACN universes / Fixtures library
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        scrollable = Gtk.ScrolledWindow()
        scrollable.set_vexpand(True)
        scrollable.set_hexpand(True)
        vbox = Gtk.VBox()
        flowbox = []
        outputs = {}
        for univ in UNIVERSES:
            vbox.pack_start(Gtk.Label(label=f"Universe {univ}"), True, True, 0)
            flowbox.append(Gtk.FlowBox())
            flowbox[-1].set_valign(Gtk.Align.START)
            flowbox[-1].set_max_children_per_line(512)
            flowbox[-1].set_selection_mode(Gtk.SelectionMode.NONE)
            for output in range(512):
                outputs[univ, output] = OutputWidget(univ, output + 1)
                flowbox[-1].add(outputs[univ, output])
            vbox.pack_start(flowbox[-1], True, True, 0)
        scrollable.add(vbox)
        stack.add_titled(scrollable, "sacn", "sACN universes")
        fixtures_library = FixturesLibrary(fixtures)
        stack.add_titled(fixtures_library, "fixtures", "Fixtures library")
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        vbox = Gtk.VBox()
        vbox.pack_start(stack_switcher, False, False, 0)
        vbox.pack_start(stack, True, True, 0)
        paned.pack2(vbox, resize=True, shrink=False)

    def channel(self, _widget):
        """Channel signal"""
        if not App().keystring:
            return
        # TODO: Validate channel
        channel = int(App().keystring)
        path = Gtk.TreePath.new_from_indices([channel - 1])
        self.treeview.set_cursor(path, None, False)
        App().keystring = ""
        App().playback.statusbar.remove_all(App().playback.context_id)

    def output(self, _widget):
        """Output signal"""
        if not App().keystring:
            return
        output = int(App().keystring)
        model, selected_channels = self.treeview.get_selection().get_selected_rows()
        for i, path in enumerate(selected_channels):
            if not model[path][2]:
                model[path][2] = "Dimmer"
            model[path][1] = str(output + i)
        App().keystring = ""
        App().playback.statusbar.remove_all(App().playback.context_id)


def focus(_widget, event):
    """Desactivate / Activate accelerators on Entry get focus

    Args:
        event (Gdk.EventFocus): Event focus
    """
    if event.in_:
        App().set_accels_for_action("app.one(1)", [])
        App().set_accels_for_action("app.two(2)", [])
        App().set_accels_for_action("app.three(3)", [])
        App().set_accels_for_action("app.four(4)", [])
        App().set_accels_for_action("app.five(5)", [])
        App().set_accels_for_action("app.six(6)", [])
        App().set_accels_for_action("app.seven(7)", [])
        App().set_accels_for_action("app.eight(8)", [])
        App().set_accels_for_action("app.nine(9)", [])
        App().set_accels_for_action("app.zero(0)", [])
        App().set_accels_for_action("app.channel", [])
    else:
        App().set_accels_for_action("app.one(1)", ["1", "KP_1"])
        App().set_accels_for_action("app.two(2)", ["2", "KP_2"])
        App().set_accels_for_action("app.three(3)", ["3", "KP_3"])
        App().set_accels_for_action("app.four(4)", ["4", "KP_4"])
        App().set_accels_for_action("app.five(5)", ["5", "KP_5"])
        App().set_accels_for_action("app.six(6)", ["6", "KP_6"])
        App().set_accels_for_action("app.seven(7)", ["7", "KP_7"])
        App().set_accels_for_action("app.eight(8)", ["8", "KP_8"])
        App().set_accels_for_action("app.nine(9)", ["9", "KP_9"])
        App().set_accels_for_action("app.zero(0)", ["0", "KP_0"])
        App().set_accels_for_action("app.channel", ["c"])
