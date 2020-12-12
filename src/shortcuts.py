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
from nino.defines import App


def setup_shortcuts():
    """Application shortcuts"""
    # General shortcuts
    App().set_accels_for_action("app.quit", ["<Control>q"])
    App().set_accels_for_action("app.patch", ["<Control>p"])
    App().set_accels_for_action("app.close_tab", ["<Control>w"])
    App().set_accels_for_action("app.undo", ["<Control>z"])
    App().set_accels_for_action("app.redo", ["<Shift><Control>z"])
    # Shortcuts desactivate when editable widget is focused
    activate_shortcuts()


def activate_shortcuts():
    """Activate shortcuts if no editable widget is focused"""
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
    App().set_accels_for_action("app.dot", ["period", "KP_Decimal"])
    App().set_accels_for_action("app.channel", ["c"])
    App().set_accels_for_action("app.thru", ["greater", "KP_Divide"])
    App().set_accels_for_action("app.output", ["o"])
    App().set_accels_for_action("app.insert", ["Insert"])


def desactivate_shortcuts():
    """Desactivate shortcuts if editable widget is focused"""
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
    App().set_accels_for_action("app.dot", [])
    App().set_accels_for_action("app.channel", [])
    App().set_accels_for_action("app.thru", [])
    App().set_accels_for_action("app.output", [])
    App().set_accels_for_action("app.insert", [])


def editable_focus(_widget, event):
    """Desactivate / Activate accelerators if editable widget get / lost focus.

    Args:
        event (Gdk.EventFocus): Event focus
    """
    if event.in_:
        desactivate_shortcuts()
    else:
        activate_shortcuts()
