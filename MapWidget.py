#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
# MapWidget.py
#
#   Drawds the MapConfig object.
#
# -----------------------------------------------------------------------------
# gpsmap - A GPSD simulator based on map positions
#   (C) 2014 Gerardo García Peña <killabytenow@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by the Free
#   Software Foundation; either version 3 of the License, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
#   for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
###############################################################################

import pygtk
pygtk.require('2.0')
import gtk
import cairo
import logging
import math

class MapWidget(gtk.DrawingArea):
    """ This class is a Drawing Area"""

    __gsignals__ = {
        "expose-event": "override",
    }
    mc       = None
    select_m = None
    select_x = None
    select_y = None
    visible  = None

    def __init__(self, mc):
        super(MapWidget, self).__init__()
        self.mc = mc
        self.select_m = None
        self.select_x = None
        self.select_y = None
        self.visible  = { "ref_points": False }

    def is_visible(self, action, element):
        self.visible[element] = not self.visible[element]
        self.redraw()
        return self.visible[element]

    def redraw(self):
        self.alloc = self.get_allocation()
        rect = gtk.gdk.Rectangle(self.alloc.x, self.alloc.y, self.alloc.width, self.alloc.height)
        if self.window is not None:
            self.window.invalidate_rect(rect, True)

    def do_expose_event(self, event):
        if self.mc is None \
        or self.mc.pixbuf is None:
            self.set_size_request(0, 0)
            return

        # set widget size based on image map
        self.set_size_request(self.mc.pixbuf.get_width(), self.mc.pixbuf.get_height())

        # create cairo surface
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        # copy image background
        cr.set_source_pixbuf(self.mc.pixbuf, 0, 0)
        cr.paint()

        # draw route
        lp = None
        for p in self.mc.route:
            if lp is None:
                cr.set_source_rgba(0, 1, 0, 0.8);
                cr.arc(p[0], p[1], 10.0, 0, 2*math.pi);
                cr.fill();
                cr.stroke()
            else:
                cr.set_source_rgba(0, 1, 0, 0.9);
                cr.move_to(lp[0], lp[1])
                cr.line_to(p[0], p[1])
                cr.stroke()
                cr.set_source_rgba(0, 1, 0, 0.4);
                cr.arc(p[0], p[1], 10.0, 0, 2*math.pi);
                cr.fill();
                cr.stroke()
            lp = p

        # draw reference points
        if self.visible["ref_points"]:
            cr.set_source_rgba(1, 0, 0, 0.6);
            cr.set_line_width(3);
            for p in [ self.mc.A, self.mc.H, self.mc.V ]:
                if p is not None:
                    cr.move_to(p[0][0] - 8, p[0][1] - 8)
                    cr.line_to(p[0][0] + 8, p[0][1] + 8)
                    cr.move_to(p[0][0] - 8, p[0][1] + 8)
                    cr.line_to(p[0][0] + 8, p[0][1] - 8)
                    cr.stroke()

        # draw selection
        if self.select_m is not None:
            cr.set_source_rgba(1, 1, 0, 0.7);
            cr.set_line_width(3);
            if self.select_m == "H" or self.select_m == "A":
                cr.move_to(0, self.select_y)
                cr.line_to(self.mc.pixbuf.get_width(), self.select_y)
                cr.stroke()
            if self.select_m == "V" or self.select_m == "A":
                cr.move_to(self.select_x, 0)
                cr.line_to(self.select_x, self.mc.pixbuf.get_height())
                cr.stroke()
            if self.select_m != "A":
                cr.move_to(self.select_x - 8, self.select_y - 8)
                cr.line_to(self.select_x + 8, self.select_y + 8)
                cr.move_to(self.select_x - 8, self.select_y + 8)
                cr.line_to(self.select_x + 8, self.select_y - 8)
                cr.stroke()

    def select_mode(self, mode, x = 0, y = 0):
        if mode is None:
            self.select_x = None
            self.select_y = None
            self.select_m = None
            self.redraw()
            return
        if mode != "H" and mode != "V" and mode != "A":
            logging.error("Bad selection mode '%s'." % mode)
            return
        self.select_m = mode
        self.select_x = x
        self.select_y = y
        self.redraw()

