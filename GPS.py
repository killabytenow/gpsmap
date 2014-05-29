#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
# GPS.py
#
#   Some GPS coordinates subs.
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


import re
import math

def sex2dec(coords):
    m = re.match(r"^\s*"                       \
                + "(?P<lad>[0-9]+)\s*[º°]\s*"   \
                + "(?P<lam>[0-9]+)\s*'\s*"      \
                + "(?P<las>[0-9]+(?:\.[0-9]*)?)\s*\"\s*" \
                + "(?P<lao>[nNsS])"
                + "\s*,\s*"
                + "(?P<lod>[0-9]+)\s*[º°]\s*"   \
                + "(?P<lom>[0-9]+)\s*'\s*"      \
                + "(?P<los>[0-9]+(?:\.[0-9]*)?)\s*\"\s*" \
                + "(?P<loo>[eEwWOO])"
                + "\s*$",
                 coords)
    if m is None:
        return (None, None)
    lao = m.group("lao").upper()
    loo = m.group("loo").upper()
    if loo == "O": loo = "W" # spanish compatibility xDDD

    la = float(m.group("lad")) + float(m.group("lam")) / 60 + float(m.group("las")) / 3600
    lo = float(m.group("lod")) + float(m.group("lom")) / 60 + float(m.group("los")) / 3600
    if lao == "S": la = la * -1.0
    if loo == "W": lo = lo * -1.0
    return (la, lo)

def dec2sex(la, lo):
    lao = "N" if la >= 0 else "S"
    la = math.fabs(la)
    lad = math.modf(la)[1]
    las, lam = math.modf(math.modf(la)[0] * 60)
    las = las * 60

    loo = "E" if lo >= 0 else "W"
    lo = math.fabs(lo)
    lod = math.modf(lo)[1]
    los, lom = math.modf(math.modf(lo)[0] * 60)
    los = los * 60

    return "%d°%d'%f\"%s, %d°%d'%f\"%s" % (lad, lam, las, lao, lod, lom, los, loo)

def distance(la1, lo1, la2, lo2):
    R = 6371.0 # earth radius (km)
    dLat = math.radians(la2 - la1)
    dLon = math.radians(lo2 - lo1)
    la1 = math.radians(la1)
    la2 = math.radians(la2)

    a = math.sin(dLat/2) * math.sin(dLat/2) \
      + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(la1) * math.cos(la2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * 1000.0 * c;

