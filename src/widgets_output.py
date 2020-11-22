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

"""Output Widget"""

import math
import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa:E402


def rounded_rectangle_fill(cr, area, radius):
    """Draw a filled rounded box

    Args:
        cr: cairo context
        area: coordinates (top, bottom, left, right)
        radius: arc's radius
    """
    a, b, c, d = area
    cr.arc(a + radius, c + radius, radius, 2 * (math.pi / 2), 3 * (math.pi / 2))
    cr.arc(b - radius, c + radius, radius, 3 * (math.pi / 2), 4 * (math.pi / 2))
    cr.arc(b - radius, d - radius, radius, 0 * (math.pi / 2), 1 * (math.pi / 2))
    cr.arc(a + radius, d - radius, radius, 1 * (math.pi / 2), 2 * (math.pi / 2))
    cr.close_path()
    cr.fill()


class OutputWidget(Gtk.Misc):
    """Output widget

    Attributes:
        universe (int): universe (1-63999)
        output (int): output number (1-512)
        level (int): output level (0-255)
        scale (float): zoom value
        width (int): widget width and height
    """

    __gtype_name__ = "OutputWidget"

    def __init__(self, universe, output):

        Gtk.Misc.__init__(self)

        self.universe = universe
        self.output = output
        self.level = 0

        self.scale = 1.0
        self.width = 32 * self.scale
        self.set_size_request(self.width, self.width)

    def do_draw(self, cr):
        """Draw widget

        Args:
            cr (cairo.Context): Used to draw with cairo
        """
        self.width = 32 * self.scale
        self.set_size_request(self.width, self.width)
        allocation = self.get_allocation()
        # Draw background
        area = (1, allocation.width - 2, 1, allocation.height - 2)
        cr.set_source_rgb(
            0.3 + (0.2 / 255 * self.level), 0.3, 0.3 - (0.3 / 255 * self.level)
        )
        rounded_rectangle_fill(cr, area, 5)
        # Draw output number
        self._draw_output_number(cr, allocation)
        # Draw Output level
        self._draw_output_level(cr, allocation)

    def _draw_output_number(self, cr, allocation):
        """Draw Output number

        Args:
            cr (cairo.Context): Used to draw with cairo
            allocation (Gdk.Rectangle): Widget's allocation
        """
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.select_font_face(
            "Cantarell Regular", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
        )
        cr.set_font_size(8 * self.scale)
        text = f"{self.output}"
        (_x, _y, width, height, _dx, _dy) = cr.text_extents(text)
        cr.move_to(
            allocation.width / 2 - width / 2, allocation.height / 4 - (height - 20) / 4
        )
        cr.show_text(text)

    def _draw_output_level(self, cr, allocation):
        """Draw Output level

        Args:
            cr (cairo.Context): Used to draw with cairo
            allocation (Gdk.Rectangle): Widget's allocation
        """
        if self.level:
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.select_font_face(
                "Cantarell Bold", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
            )
            cr.set_font_size(8 * self.scale)
            text = str(self.level)
            (_x, _y, width, height, _dx, _dy) = cr.text_extents(text)
            cr.move_to(
                allocation.width / 2 - width / 2,
                allocation.height / 2 - (height - 20) / 2,
            )
            cr.show_text(text)
