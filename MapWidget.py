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
import GPS
import gobject

class MapWidget(gtk.DrawingArea):
    """ This class is a Drawing Area"""

    __gsignals__ = {
        "expose-event": "override",
    }
    mc        = None
    select_m  = None
    select_x  = None
    select_y  = None
    visible   = None
    ruler     = None
    cp_radius = None

    def __init__(self, mc):
        super(MapWidget, self).__init__()
        self.cp_radius = 0
        self.mc = mc
        self.select_m = None
        self.select_x = None
        self.select_y = None
        self.visible  = {
            "ref_points": False,
            "points":     False,
            "route":      False,
            "background": 2,
        }
        gobject.timeout_add(100, self.do_animation)

    def bg_visible(self, action, value):
        self.visible["background"] = value.get_current_value()
        self.redraw()

    def is_visible(self, action, element):
        self.visible[element] = not self.visible[element]
        self.redraw()
        return self.visible[element]

    def ruler_set_start(self, x, y):
        self.ruler = [ x, y, x, y ]
        self.redraw()

    def ruler_set_end(self, x, y):
        self.ruler[2] = x
        self.ruler[3] = y
        self.redraw()

    def ruler_unset(self):
        self.ruler = None
        self.redraw()

    def redraw(self):
        self.alloc = self.get_allocation()
        rect = gtk.gdk.Rectangle(self.alloc.x, self.alloc.y, self.alloc.width, self.alloc.height)
        if self.window is not None:
            self.window.invalidate_rect(rect, True)

    def do_animation(self):
        if self.mc is None or self.mc.curr_xy is None:
            return True

        if self.cp_radius is None or self.cp_radius > 10:
            self.cp_radius = 0
        else:
            self.cp_radius = self.cp_radius + 1

        self.redraw()
        return True
        self.alloc = self.get_allocation()
        rect = gtk.gdk.Rectangle(
            self.alloc.x + int(self.mc.curr_xy[0]) - 15,
            self.alloc.y + int(self.mc.curr_xy[1]) - 15,
            40, 40)
        if self.window is not None:
            self.window.invalidate_rect(rect, True)
        return True

    def do_draw(self, cr, draw_curr_xy):
        # copy image background
        cr.set_source_surface(self.mc.bg_surface, 0, 0)
        cr.paint()
        if self.visible["background"] != 2:
            cr.set_source_rgba(0, 0, 0, .5 if self.visible["background"] == 1 else .9)
            cr.rectangle(0, 0, self.mc.bg_w - 1, self.mc.bg_h - 1)
            cr.fill()
            cr.stroke()

        # draw route
        if self.visible["route"] and self.mc.route is not None:
            lp = None
            for p in self.mc.route:
                if lp is None:
                    cr.set_source_rgba(0, 1, 0, 0.8)
                    cr.arc(p[0], p[1], 10.0, 0, 2*math.pi)
                    cr.fill()
                    cr.stroke()
                else:
                    cr.set_source_rgba(0, 1, 0, 0.9)
                    cr.move_to(lp[0], lp[1])
                    cr.line_to(p[0], p[1])
                    cr.stroke()
                    cr.set_source_rgba(0, 1, 0, 0.4)
                    cr.arc(p[0], p[1], 10.0, 0, 2*math.pi)
                    cr.fill()
                    cr.stroke()
                lp = p

        # draw reference points
        if self.visible["ref_points"]:
            for p in [ self.mc.A, self.mc.H, self.mc.V ]:
                if p is not None:
                    cr.set_source_rgba(0, 0, 0, 1)
                    cr.set_line_width(4)
                    cr.move_to(p[0][0] - 8 + 1, p[0][1] - 8 + 1)
                    cr.line_to(p[0][0] + 8 + 1, p[0][1] + 8 + 1)
                    cr.move_to(p[0][0] - 8 + 1, p[0][1] + 8 + 1)
                    cr.line_to(p[0][0] + 8 + 1, p[0][1] - 8 + 1)
                    cr.stroke()
                    cr.set_line_width(3)
                    cr.set_source_rgba(1, 0, 0, 0.8)
                    cr.move_to(p[0][0] - 8, p[0][1] - 8)
                    cr.line_to(p[0][0] + 8, p[0][1] + 8)
                    cr.move_to(p[0][0] - 8, p[0][1] + 8)
                    cr.line_to(p[0][0] + 8, p[0][1] - 8)
                    cr.stroke()

        if self.visible["points"]:
            for n in self.mc.points.keys():
                x, y = self.mc.points[n][0], self.mc.points[n][1]
                cr.set_source_rgba(0, 0, 1, .8)
                cr.set_line_width(2)
                cr.arc(x, y, 6.0, 0, 2*math.pi)
                cr.stroke()
                cr.arc(x, y, 4.0, 0, 2*math.pi)
                cr.fill()
                cr.stroke()
                xbearing, ybearing, width, height, xadvance, yadvance = (cr.text_extents(n))
                cr.set_source_rgba(0, 0, 0, 1)
                cr.move_to(x + 1 - width/2, y + 1 + height)
                cr.show_text(n)
                cr.set_source_rgba(1, 1, 1, 1)
                cr.move_to(x - width/2, y + height)
                cr.show_text(n)
                cr.stroke()

        # draw selection
        if self.select_m is not None:
            if self.select_m == "H" or self.select_m == "A":
                cr.set_source_rgba(0, 0, 0, 1)
                cr.set_line_width(1)
                cr.move_to(0, self.select_y + 1)
                cr.line_to(self.mc.bg_w, self.select_y + 1)
                cr.stroke()
                cr.set_source_rgba(1, 1, 0, 0.7)
                cr.set_line_width(3)
                cr.move_to(0, self.select_y)
                cr.line_to(self.mc.bg_w, self.select_y)
                cr.stroke()
            if self.select_m == "V" or self.select_m == "A":
                cr.set_source_rgba(0, 0, 0, 1)
                cr.set_line_width(1)
                cr.move_to(self.select_x + 1, 0)
                cr.line_to(self.select_x + 1, self.mc.bg_h)
                cr.stroke()
                cr.set_source_rgba(1, 1, 0, 0.7)
                cr.set_line_width(3)
                cr.move_to(self.select_x, 0)
                cr.line_to(self.select_x, self.mc.bg_h)
                cr.stroke()
            if self.select_m == "P":
                cr.set_source_rgba(0, 0, 1, .4)
                cr.set_line_width(2)
                cr.arc(self.select_x, self.select_y, 4.0, 0, 2*math.pi)
                cr.stroke()
                cr.arc(self.select_x, self.select_y, 2.0, 0, 2*math.pi)
                cr.fill()
                cr.stroke()
            elif self.select_m != "A":
                cr.set_source_rgba(0, 0, 0, 1)
                cr.set_line_width(1)
                cr.move_to(self.select_x - 8 + 1, self.select_y - 8 + 1)
                cr.line_to(self.select_x + 8 + 1, self.select_y + 8 + 1)
                cr.move_to(self.select_x - 8 + 1, self.select_y + 8 + 1)
                cr.line_to(self.select_x + 8 + 1, self.select_y - 8 + 1)
                cr.stroke()
                cr.set_source_rgba(1, 1, 0, 0.7)
                cr.set_line_width(3)
                cr.move_to(self.select_x - 8, self.select_y - 8)
                cr.line_to(self.select_x + 8, self.select_y + 8)
                cr.move_to(self.select_x - 8, self.select_y + 8)
                cr.line_to(self.select_x + 8, self.select_y - 8)
                cr.stroke()

        # draw ruler
        if self.ruler is not None:
                cr.set_line_width(6)
                cr.set_source_rgba(0, 0, 0, 1)
                cr.move_to(self.ruler[0], self.ruler[1])
                cr.line_to(self.ruler[2], self.ruler[3])
                cr.stroke()
                cr.set_line_width(4)
                cr.set_source_rgba(0, 1, 0, 1)
                cr.set_dash([ 5.0 ], 0)
                cr.move_to(self.ruler[0], self.ruler[1])
                cr.line_to(self.ruler[2], self.ruler[3])
                cr.stroke()
                a = self.mc.pixel2coords(self.ruler[0], self.ruler[1])
                b = self.mc.pixel2coords(self.ruler[2], self.ruler[3])
                if a is None or b is None:
                    distance = "???"
                else:
                    distance = "%.2f m" % GPS.distance(a[0], a[1], b[0], b[1])
                xbearing, ybearing, width, height, xadvance, yadvance = (cr.text_extents(distance))
                x = ((self.ruler[0] + self.ruler[2]) / 2)
                y = ((self.ruler[1] + self.ruler[3]) / 2)
                cr.set_source_rgba(0, 0, 0, 0.6)
                cr.set_line_width(1)
                cr.rectangle(x - width, y - height, width*2, height*2)
                cr.fill()
                cr.stroke()
                cr.set_source_rgba(0, 0, 0, 1)
                cr.move_to(x + 1 - width/2, y + 1)
                cr.show_text(distance)
                cr.set_source_rgba(1, 1, 1, 1)
                cr.move_to(x - width/2, y)
                cr.show_text(distance)
                cr.set_dash([], 0)
                cr.stroke()

        # draw curr_xy
        if self.mc.curr_xy is not None and draw_curr_xy:
            x, y = self.mc.curr_xy[0], self.mc.curr_xy[1]
            for i in range(1, 4):
                cr.set_line_width(5 - i)
                cr.set_source_rgba(1, 0, 1, ((float(self.cp_radius) / 15.0)))
                cr.arc(x, y, (float(10 - self.cp_radius) * float(i) / 4.0) * 3 + 2, 0, 2*math.pi)
                cr.stroke()
            cr.set_source_rgba(1, 0, 1, 1)
            cr.arc(x, y, 2.5, 0, 2*math.pi)
            cr.fill()
            cr.stroke()

    def do_expose_event(self, event):
        if self.mc is None \
        or self.mc.bg_surface is None:
            self.set_size_request(0, 0)
            return

        # set widget size based on image map
        self.set_size_request(self.mc.bg_w, self.mc.bg_h)

        # create cairo surface
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        self.do_draw(cr, True)


    def select_mode(self, mode, x = 0, y = 0):
        if mode is None:
            self.select_x = None
            self.select_y = None
            self.select_m = None
            self.redraw()
            return
        if mode != "H" and mode != "V" and mode != "A" and mode != "P":
            logging.error("Bad selection mode '%s'." % mode)
            return
        self.select_m = mode
        self.select_x = x
        self.select_y = y
        self.redraw()

    def save_png(self, path):
        logging.info("\t%s: Saving image (%d, %d) pixels" % (path, self.mc.bg_w, self.mc.bg_h))
        logging.info("\t%s: Creating cairo context and surface" % (path))
        dst_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.mc.bg_w, self.mc.bg_h)
        dst_ctx = cairo.Context(dst_surface)

        logging.info("\t%s: drawing" % (path))
        self.do_draw(dst_ctx, False)

        logging.info("\t%s: writing" % (path))
        dst_surface.write_to_png(path)

