#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
# MapConfig.py
#
#   The map document model.
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
import json
import logging
import math

import GPS
import Vect

class MapConfig(object):
    # config
    filename   = None
    imgpath    = None
    A          = None
    H          = None
    V          = None
    route      = None
    points     = None
    walk_speed = None

    # calculated properties
    to       = None
    raca     = None
    dflo     = None
    dfla     = None
    pixbuf   = None
    curr_pos = None
    curr_xy  = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.route    = [ ]
        self.points   = { }
        self.filename = None
        self.imgpath  = None
        self.A        = None
        self.H        = None
        self.V        = None
        self.route    = None
        self.to       = None
        self.raca     = None
        self.dflo     = None
        self.dfla     = None
        self.pixbuf   = None
        self.walk_speed = 4000  # humans with laptop walk at 4km/h

    def json_read(self, config):
        self.reset()

        j = json.loads(config)

        # load img config
        if j["imgpath"] is not None:
            self.map_load(j["imgpath"])
        else:
            self.map_unset()

        # walk speed
        if "walk_speed" in j:
            self.walk_speed = j["walk_speed"]

        # load reference points
        if j["A"] is not None:
            la, lo = GPS.sex2dec(j["A"]["coord"])
            self.set_ref("A", j["A"]["xy"][0], j["A"]["xy"][1], la, lo)
        else:
            self.unset_ref("A")
        if j["H"] is not None:
            la, lo = GPS.sex2dec(j["H"]["coord"])
            self.set_ref("H", j["H"]["xy"][0], j["H"]["xy"][1], la, lo)
        else:
            self.unset_ref("H")
        if j["V"] is not None:
            la, lo = GPS.sex2dec(j["V"]["coord"])
            self.set_ref("V", j["V"]["xy"][0], j["V"]["xy"][1], la, lo)
        else:
            self.unset_ref("V")

        # load last route
        self.route = j["route"]

    def json_write(self):
        return json.dumps({
            "imgpath": self.imgpath,
            "A": { "coord": GPS.dec2sex(self.A[1][1], self.A[1][0]), "xy": self.A[0] }
                 if self.A is not None else None,
            "H": { "coord": GPS.dec2sex(self.H[1][1], self.H[1][0]), "xy": self.H[0] }
                 if self.H is not None else None,
            "V": { "coord": GPS.dec2sex(self.V[1][1], self.V[1][0]), "xy": self.V[0] }
                 if self.V is not None else None,
            "route":   self.route,
            "walk_speed": self.walk_speed,
        }, indent = 4)

    def map_load(self, mapfile):
        logging.info("Loading map image '%s'." % mapfile)
        self.imgpath = mapfile
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(mapfile)

    def map_unset(self):
        logging.info("Unset map image.")
        self.imgpath = None
        if self.pixbuf is not None:
            self.pixbuf.destroy()
        self.pixbuf = None

    def point_add(self, name, x, y):
        self.points[name] = [ x, y ]

    def unset_ref(self, pn):
        if   pn == "A": self.A = None
        elif pn == "H": self.H = None
        elif pn == "V": self.V = None
        else:
            logging.error("Bad reference point '%s'.", pn)
            return
        self.to   = None
        self.raca = None
        self.dflo = None
        self.dfla = None

    def set_ref(self, pn, x, y, la, lo):
        if   pn == "A": self.A = [ Vect.vect(x, y), Vect.vect(lo, la) ]
        elif pn == "H": self.H = [ Vect.vect(x, y), Vect.vect(lo, la) ]
        elif pn == "V": self.V = [ Vect.vect(x, y), Vect.vect(lo, la) ]
        else:
            logging.error("Bad reference point '%s'.", pn)
            return

        # check we have everything that we need before starting calculations
        if self.A is None or self.H is None or self.V is None:
            return

        # do calculus (we have all needed data)
        # 1) Calculate angle between an horizontal vector and 'AH' vector
        self.to = Vect.vangle(Vect.vsub(self.H[1], self.A[1]), Vect.vect(1, 0))
        logging.info("angle(AH, (1,0)) = %f rad (%fº)" % (self.to, math.degrees(self.to)))

        # 2) Calculate 'raca' (angle between AH ^ AV)
        self.raca = Vect.vangle(Vect.vsub(self.H[1], self.A[1]), Vect.vsub(self.V[1], self.A[1]))
        logging.info("angle(AH, AV) = %f" % math.degrees(self.raca))

        # 2) calculate 'dflo' and 'dfla' factors (pixels to dec degrees)
        logging.info("|ha|º  = %f" % Vect.vmod(Vect.vsub(self.H[1], self.A[1])))
        logging.info("|ha|px = %f" % Vect.vmod(Vect.vsub(self.H[0], self.A[0])))
        logging.info("|va|º  = %f" % Vect.vmod(Vect.vsub(self.V[1], self.A[1])))
        logging.info("|va|px = %f" % Vect.vmod(Vect.vsub(self.V[0], self.A[0])))
        self.dflo = Vect.vmod(Vect.vsub(self.H[1], self.A[1])) \
                  / Vect.vmod(Vect.vsub(self.H[0], self.A[0]))
        self.dfla = Vect.vmod(Vect.vsub(self.V[1], self.A[1])) \
                  / Vect.vmod(Vect.vsub(self.V[0], self.A[0]))


        cri = Vect.vangle(Vect.vsub(self.H[0], self.A[0]), Vect.vsub(self.V[0], self.A[0]))
        logging.info("angle(ex, ey)   = %f" % math.degrees(cri))
        self.dflo = self.dflo * math.sin(self.raca)
        self.dfla = self.dfla * math.sin(self.raca)

        logging.info("dflo = %f" % self.dflo)
        logging.info("dfla = %f" % self.dfla)

    def pixel2coords(self, x, y):
        if x < 0 or x > self.pixbuf.get_width() \
        or y < 0 or y > self.pixbuf.get_height():
            return None
        if self.A is None or self.H is None or self.V is None:
            return None

        sin = math.sin(self.to)
        cos = math.cos(self.to)

        x1 = (x - self.A[0][0]) * self.dflo
        y1 = (y - self.A[0][1]) * self.dfla
        x, y = x1, y1

        x1 = x / math.sin(self.raca) + y * math.cos(self.raca)
        y1 = y
        x, y = x1, y1

        x1 = (y * sin - x * cos) / (sin*sin + cos*cos)
        y1 = (y * cos + x * sin) / (sin*sin + cos*cos)
        x, y = x1, y1

        v = Vect.vsum(Vect.vect(x1, y1), self.A[1])

        return [v[1], v[0]]

    def route_point_xy(self, n):
        return (self.route[n][0], self.route[n][1])

    def route_point_coords(self, n):
        return self.pixel2coords(self.route[n][0], self.route[n][1])

    def set_curr_pos(self, x, y):
        self.curr_xy = [x, y]
        self.curr_pos = self.pixel2coords(x, y)
        return self.curr_pos

    def route_add(self, x, y):
        self.route.append([x, y])

    def load(self, configfile):
        self.filename = configfile
        f = open(configfile, "r")
        self.json_read(f.read())
        f.close()

    def save(self, configfile):
        self.filename = configfile
        f = open(configfile, "w")
        f.write(self.json_write())
        f.close()

    def route_unset(self):
        self.route = []

    def route_save_kml(self, routefile):
        if routefile is None or routefile == "":
            self.route_file = \
                "%s.kml" % (self.configfile if self.configfile is not None else "route")
        f = open(routefile, "w")
        f.write(
"""<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Placemark><name>route</name>
<description>gpsmap route</description>
<LineString>
<coordinates>
""")
        for p in self.route:
            c = self.pixel2coords(p[0], p[1])
            f.write("%f,%f\n" % (c[1], c[0]))
        f.write(
"""</coordinates>
</LineString>
</Placemark></Document>
</kml>
""")


