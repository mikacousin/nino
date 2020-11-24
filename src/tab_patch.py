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

import nino.shortcuts as shortcuts
from nino.console import Fixture
from nino.defines import App, MAX_CHANNELS, UNIVERSES
from nino.paths import get_fixtures_dir
from nino.widgets_output import OutputWidget


class FixturesLibrary(Gtk.VBox):
    """Fixtures library

    Attributes:
        show_fixtures (Fixtures): Fixtures in the show
        fixtures (Gtk.TreeStore): Fixtures library TreeStore
        search_entry (Gtk.SearchEntry): Search Entry
        filter (Gtk.TreeModel): fixtures filter
        view (Gtk.TreeView): fixtures view
    """

    def __init__(self, fixtures):
        Gtk.VBox.__init__(self)

        self.show_fixtures = fixtures

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
        self.search_entry.connect("focus-in-event", shortcuts.editable_focus)
        self.search_entry.connect("focus-out-event", shortcuts.editable_focus)
        self.filter = self.fixtures.filter_new()
        self.filter.set_visible_column(0)
        self.pack_start(self.search_entry, False, False, 0)
        # Fixtures treeview
        self.view = Gtk.TreeView(model=self.filter)
        self.view.connect("row-activated", self.fixtures_activated)
        renderer = Gtk.CellRendererText()
        self.view.append_column(Gtk.TreeViewColumn("Fixtures", renderer, text=1))
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
            path.up()
            fixture_manufacturer = model[path][1]
            label = f"{fixture_model} {fixture_mode}"
            # If fixture is already in show, doesn't add it
            found = False
            for child in self.show_fixtures.flowbox.get_children():
                if child.get_children()[0].get_label() == label:
                    found = True
                    break
            if not found:
                fixture = get_fixture(
                    manufacturer=fixture_manufacturer,
                    model=fixture_model,
                    mode=fixture_mode,
                )
                App().fixtures.append(fixture)
                button = FixtureButton()
                button.set_label(label)
                button.fixture = fixture
                button.connect("clicked", self.show_fixtures.clicked)
                self.show_fixtures.flowbox.add(button)
                self.show_fixtures.flowbox.show_all()


def get_fixture(manufacturer=None, model=None, mode=None):
    """Find fixture with his name

    Args:
        manufacturer (str): Manufacturer name
        model (str): Model name
        mode (str): Mode name

    Returns:
        fixture (Fixture): fixture
    """
    path = get_fixtures_dir()
    with open(os.path.join(path, "index.json"), "r") as index_file:
        index = json.load(index_file)
    file_name = None
    for file_name, fixture in index.items():
        if (
            fixture.get("manufacturer") == manufacturer
            and fixture.get("model_name") == model
            and fixture.get("mode") == mode
        ):
            break
    with open(os.path.join(path, file_name), "r") as fixture_file:
        fixture_json = json.load(fixture_file)
    fixture = Fixture(fixture_json.get("name"))
    fixture.manufacturer = fixture_json.get("manufacturer")
    fixture.model_name = fixture_json.get("model_name")
    fixture.parameters = fixture_json.get("parameters")
    fixture.modes = fixture_json.get("modes")
    return fixture


class FixtureButton(Gtk.Button):
    """Button for fixtures

    Attributes:
        fixture (Fixture): fixture or None
    """

    def __init__(self):
        Gtk.Button.__init__(self)
        self.fixture = None


class Fixtures(Gtk.ScrolledWindow):
    """Fixtures in the show

    Attributes:
        channels (Gtk.TreeView): Channels treeview
    """

    def __init__(self, channels):
        Gtk.ScrolledWindow.__init__(self)

        # Fixtures
        fixtures = App().fixtures

        self.channels = channels

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        for fixture in fixtures:
            button = FixtureButton()
            button.set_label(fixture.name)
            button.fixture = fixture
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
            model[path][1] = ""
            channel = model[path][0]
            output = 0
            universe = 0
            fixture = button.fixture
            App().patch.patch_channel(channel, output, universe, fixture)


class SacnWidget(Gtk.ScrolledWindow):
    """sACN View Widget"""

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_vexpand(True)
        self.set_hexpand(True)
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
        self.add(vbox)


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
        scrollable = self.create_channels_list()
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
        stack.add_titled(SacnWidget(), "sacn", "sACN universes")
        stack.add_titled(FixturesLibrary(fixtures), "fixtures", "Fixtures library")
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        vbox = Gtk.VBox()
        vbox.pack_start(stack_switcher, False, False, 0)
        vbox.pack_start(stack, True, True, 0)
        paned.pack2(vbox, resize=True, shrink=False)

    def create_channels_list(self):
        """Create Channels list

        Returns:
            scrollable (Gtk.ScrolledWindow)
        """
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
        return scrollable

    def channel(self, _widget):
        """Channel signal"""
        if not App().keystring or not App().keystring().isdigit():
            App().keystring = ""
            App().playback.statusbar.remove_all(App().playback.context_id)
            return
        channel = int(App().keystring)
        path = Gtk.TreePath.new_from_indices([channel - 1])
        self.treeview.set_cursor(path, None, False)
        App().keystring = ""
        App().playback.statusbar.remove_all(App().playback.context_id)

    def output(self, _widget):
        """Output signal"""
        if not validate_entry(App().keystring):
            App().keystring = ""
            App().playback.statusbar.remove_all(App().playback.context_id)
            return
        output, universe = parse_entry(App().keystring)
        if not universe:
            App().keystring = ""
            App().playback.statusbar.remove_all(App().playback.context_id)
            return
        model, selected_channels = self.treeview.get_selection().get_selected_rows()
        footprint = 0
        if not verify_fixture(model, selected_channels):
            print("No multipatch with different fixtures")
            return
        for i, path in enumerate(selected_channels):
            fixture = get_fixture_by_name(model, path)
            channel = model[path][0]
            if output:
                real_output = output + (i * footprint)
            else:
                # Universe change, no Output in entry. So, try to find one
                real_output = App().patch.channels[channel].output
                if not real_output:
                    App().keystring = ""
                    App().playback.statusbar.remove_all(App().playback.context_id)
                    return
            footprint = App().patch.patch_channel(
                channel, real_output, universe, fixture
            )
            # Update Channels list
            univ = ""
            if universe != UNIVERSES[0]:
                univ = f".{universe}"
            if footprint > 1:
                text = f"{real_output}{univ}-{real_output + footprint - 1}{univ}"
            else:
                text = f"{real_output}{univ}"
            model[path][1] = text
        App().keystring = ""
        App().playback.statusbar.remove_all(App().playback.context_id)


def get_fixture_by_name(model, path):
    """Get fixture by name

    Args:
        model (Gtk.TreeModel): Model with datas
        path (Gtk.TreePath): row

    Returns:
        fixture
    """
    if not model[path][2]:
        # No fixture, use Dimmer
        model[path][2] = "Dimmer"
        fixture = App().fixtures[0]
    else:
        # Find fixture
        for fixture in App().fixtures:
            fixture_model = fixture.model_name
            try:
                mode = fixture.modes[0].get("name")
            except IndexError:
                mode = ""
            if mode:
                name = f"{fixture_model} {mode}"
            else:
                name = f"{fixture_model}"
            if name == model[path][2]:
                break
    return fixture


def validate_entry(text):
    """Validate entry

    Args:
        text (str): text entry

    Returns:
        (bool)
    """
    if not text or not text.replace(".", "", 1).isdigit():
        return False
    return True


def parse_entry(text):
    """Parse entry

    Args:
        text (str): Text entry

    Returns:
        output (int), universe (int)
    """
    if "." in text:
        if text[0] == ".":
            # Change universe
            output = None
            universe = int(text[1:])
        else:
            # Output.Universe
            split = text.split(".")
            output = int(split[0])
            universe = int(split[1])
    else:
        # Output in first universe
        output = int(text)
        universe = UNIVERSES[0]
    if universe not in UNIVERSES:
        universe = 0
    return output, universe


def verify_fixture(model, selected_channels):
    """Verify if all fixtures are the same

    Args:
        model (Gtk.TreeModel): Model with datas
        selected_channels (Gtk.TreePath): Channels

    Returns:
        (bool) True if Ok
    """
    ref = None
    for path in selected_channels:
        if not ref:
            ref = model[path][2]
        else:
            if model[path][2] != ref:
                return False
    return True
