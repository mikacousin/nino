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
"""Wheel controller widget"""
import math
import cairo

from gi.repository import Gdk, GLib, GObject, Gtk  # noqa:E402


class WheelWidget(Gtk.DrawingArea):
    """Wheel widget, inherits from Gtk.DrawingArea"""

    __gtype_name__ = "WheelWidget"

    __gsignals__ = {
        "moved": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (
                Gdk.ScrollDirection,
                int,
            ),
        ),
        "clicked": (GObject.SignalFlags.ACTION, None, ()),
    }

    def __init__(self, param):
        Gtk.DrawingArea.__init__(self)

        self.parameter = param
        self.angle = 0
        self.step = 0
        self.pressed = False

        # Widget dimensions
        self.scale = 1.5
        self.width = 20 * self.scale
        self.height = 80 * self.scale
        self.set_size_request(self.width, self.height)

        self.add_events(Gdk.EventMask.SCROLL_MASK)
        self.connect("scroll-event", self.on_scroll)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_press)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.connect("button-release-event", self.on_release)
        self.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.connect("motion-notify-event", self.on_motion)

    def on_timeout(self, _data):
        """Until mouse button pressed

        Returns:
            (bool): True=continue, False=stop
        """
        if not self.pressed:
            return False
        if self.step > 0:
            self.emit("moved", Gdk.ScrollDirection.UP, self.step)
        elif self.step < 0:
            self.emit("moved", Gdk.ScrollDirection.DOWN, abs(self.step))
        self.queue_draw()
        return True

    def on_release(self, _tgt, _event):
        """Mouse button released"""
        self.pressed = False
        self.emit("clicked")

    def on_press(self, _tgt, event):
        """Mouse button pressed

        Args:
            event (Gdk.EventButton) : Button pressed event
        """
        self.pressed = True
        self.new_step(event)
        GLib.timeout_add(100, self.on_timeout, None)

    def on_motion(self, _tgt, event):
        """Track mouse to move wheel

        Args:
            event: Motion event
        """
        if self.pressed:
            self.new_step(event)

    def new_step(self, event):
        """Set step on new mouse position

        Args:
            event: an event with mouse position
        """
        # Center
        y_center = self.get_allocation().height / 2
        # Actual position
        y_now = event.y
        # Distance beetwen center and actual position
        delta = y_center - y_now
        if delta > y_center:
            delta = y_center
        elif delta < -y_center:
            delta = -y_center
        if delta > 0:
            self.step = int((delta / y_center) * 4) + 1
        elif delta < 0:
            self.step = int((delta / y_center) * 4) - 1

    def on_scroll(self, _widget, event):
        """On scroll wheel event

        Args:
            event (Gdk.EventScroll): Scroll event
        """
        accel_mask = Gtk.accelerator_get_default_mod_mask()
        step = 4
        if event.state & accel_mask == Gdk.ModifierType.SHIFT_MASK:
            step = 1
        (scroll, direction) = event.get_scroll_direction()
        if scroll and direction == Gdk.ScrollDirection.UP:
            self.emit("moved", Gdk.ScrollDirection.UP, step)
        if scroll and direction == Gdk.ScrollDirection.DOWN:
            self.emit("moved", Gdk.ScrollDirection.DOWN, step)

    def do_moved(self, direction, step):
        """On moved event

        Args:
            direction (Gdk.ScrollDirection): Direction
            step (int): increment or decrement value
        """
        if direction == Gdk.ScrollDirection.UP:
            self.angle += step
        elif direction == Gdk.ScrollDirection.DOWN:
            self.angle -= step
        if self.angle > 10:
            self.angle -= 10
        elif self.angle < 0:
            self.angle += 10
        self.queue_draw()

    def do_draw(self, cr):
        """Draw Controller

        Args:
            cr (cairo.Context): Used to draw with cairo
        """
        # To center widget horizontally
        offset = int((self.get_allocation().width - self.width) / 2)

        line_width = self.scale / 2
        cr.set_line_width(line_width)
        cr.set_line_cap(cairo.LineCap.BUTT)
        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        cr.translate(0, self.height / 2)
        for angle in range(self.angle, self.angle + 190, 10):
            height = math.cos(math.radians(angle)) * (self.height / 2)
            cr.move_to(offset + line_width * 3, height)
            cr.line_to(offset + self.width - (line_width * 3), height)
            cr.stroke()
        line_width = 3 * (self.scale / 2)
        cr.set_line_width(line_width)
        cr.set_line_cap(cairo.LineCap.ROUND)
        cr.set_source_rgba(0.5, 0.3, 0.0, 1.0)
        cr.move_to(offset + line_width / 2, 0)
        cr.line_to(offset + self.width - (line_width / 2), 0)
        cr.stroke()
