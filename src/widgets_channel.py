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
"""Channel Widget"""
import cairo

from gi.repository import Gdk, Gtk  # noqa: E402

from nino.defines import App


class ChannelWidget(Gtk.Misc):
    """Channel widget"""

    __gtype_name__ = "ChannelWidget"

    def __init__(self, channel, device=None):
        Gtk.Misc.__init__(self)

        self.channel = channel
        self.device = device
        self.scale = 1.0
        self.color_level = {"red": 0.9, "green": 0.9, "blue": 0.9}

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

        self.set_size_request(80, 80)

    def on_click(self, widget, event):
        """Select / Unselect widget

        Args:
            widget (ChannelWidget): widget
            event (Gdk.EventButton): event
        """
        accel_mask = Gtk.accelerator_get_default_mod_mask()
        flowboxchild = widget.get_parent()
        flowbox = flowboxchild.get_parent()
        flowboxchild.grab_focus()
        active = App().get_active_window()
        page = active.notebook.get_current_page()
        tab = active.notebook.get_nth_page(page)
        if event.state & accel_mask == Gdk.ModifierType.SHIFT_MASK:
            # Shift + Click : Thru
            App().keystring = str(self.channel)
            tab.emit("thru")
            return
        if flowboxchild.is_selected():
            flowbox.unselect_child(flowboxchild)
        else:
            flowbox.select_child(flowboxchild)
        tab.last_chan = self.channel - 1

    def do_draw(self, cr):
        """Draw widget

        Args:
            cr (cairo.Context): Used to draw with cairo
        """
        # Set widget dimension
        width = 80 * self.scale
        if self.device and self.device.fixture.name != "Dimmer" and self.device.output:
            height = 130 * self.scale
        else:
            height = width
        self.set_size_request(width, height)
        allocation = self.get_allocation()
        if not self.device or self.device.fixture.name == "Dimmer":
            allocation.height = width
        # allocation.width = width

        # Draw background
        if self.get_parent().is_selected():
            cr.set_source_rgb(0.6, 0.4, 0.1)
            cr.rectangle(0, 0, allocation.width, allocation.height)
            cr.fill()
        cr.set_source_rgba(0.3, 0.3, 0.3, 1)
        cr.rectangle(0, 0, allocation.width, allocation.height)
        cr.stroke()
        background = Gdk.RGBA()
        background.parse("#33393B")
        cr.set_source_rgba(*list(background))
        cr.rectangle(4, 4, allocation.width - 8, allocation.height - 8)
        cr.fill()
        # Rectangle for channel number
        if self.get_parent().is_selected():
            cr.set_source_rgb(0.4, 0.4, 0.4)
        else:
            cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(4, 4, allocation.width - 8, 18 * self.scale)
        cr.fill()
        # Channel number
        cr.set_source_rgb(0.9, 0.6, 0.2)
        cr.select_font_face(
            "Cantarell Regular", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
        )
        cr.set_font_size(12 * self.scale)
        text = str(self.channel)
        (_, _, text_width, _, _, _) = cr.text_extents(text)
        cr.move_to(allocation.width / 2 - text_width / 2, 15 * self.scale)
        cr.show_text(str(self.channel))
        # Device informations if not a dimmer
        if self.device and self.device.fixture.name != "Dimmer" and self.device.output:
            self._draw_device(cr, width, allocation)

    def _draw_device(self, cr, width, allocation):
        """Draw device informations

        Args:
            cr (cairo.Context): Used to draw with cairo
            width (int): widget width
            allocation (Gdk.Rectangle): Widget's allocation
        """
        # Background
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.rectangle(4, width - 6, allocation.width - 8, 18 * self.scale)
        cr.fill()
        # Device name
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.select_font_face(
            "Cantarell Regular", cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL
        )
        cr.set_font_size(9 * self.scale)
        text = self.device.fixture.model_name
        if len(text) > 15:
            text = text[:13] + "..."
        (_, _, text_width, _, _, _) = cr.text_extents(text)
        cr.move_to(allocation.width / 2 - text_width / 2, 83 * self.scale)
        cr.show_text(text)
        text = self.device.fixture.mode.get("name")
        if len(text) > 15:
            text = text[:13] + "..."
        (_, _, text_width, _, _, _) = cr.text_extents(text)
        cr.move_to(allocation.width / 2 - text_width / 2, 90 * self.scale)
        cr.show_text(text)
