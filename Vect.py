#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
# Vect.py
#
#   Some simple 2D vector operations.
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


import math

def vect(vx, vy):
    return [ float(vx), float(vy) ]

def vsub(va, vb):
    return [ vb[0] - va[0], vb[1] - va[1] ]

def vsum(va, vb):
    return [ vb[0] + va[0], vb[1] + va[1] ]

def vmod(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1])

def vangle(a, b):
    return math.acos((a[0]*b[0] + a[1]*b[1]) / (vmod(a) * vmod(b)))

def vangle2(a, b):
    return math.atan2(b[1], b[0]) - math.atan2(a[1], a[0])

def vstr(v):
    return "(%f, %f)" % (v[0], v[1])


