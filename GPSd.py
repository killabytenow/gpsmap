#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
# GPSd.py
#
#   A gpsd server simulator
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

import json
import logging
import threading
import time
import select
import socket

class GPSdThread(threading.Thread):
    device = '/dev/ojetegps'
    host = ''
    port = 2947
    quit = False
    time_started = None

    def __init__(self, mc):
        super(GPSdThread, self).__init__()
        self.quit = False
        self.mc = mc
        self.time_started = time.gmtime()

    def get_time(self, t = None):
        if t is None:
            t = time.gmtime()
        return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", t)

    def get_cmd_VERSION(self, params):
        return "%s\r\n" % \
            json.dumps({
                "class"       : "VERSION",
                "version"     : "69dev",
                "rev"         : "ojete",
                "proto_major" : 3,
                "proto_minor" : 1,
            })

    def get_cmd_GST(self):
        return "%s\r\n" % json.dumps({
                "class"    : "GST",
                "tag"      : "GST",
                "device"   : self.device,
                "time"     : self.get_time(),
                "rms"      : 4.100,
                "major"    : 13.000,
                "minor"    : 8.300,
                "orient"   : 133.000,
                "lat"      : 11.000,
                "lon"      : 11.000,
                "alt"      : 46.000,
            })

    def get_cmd_TPV(self):
        return "%s\r\n" % json.dumps({
                "class"  : "TPV",
                "tag"    : "RMC",
                "device" : self.device,
                "mode"   : 3,
                "time"   : self.get_time(),
                "ept"    : 0.005,
                "lat"    : self.mc.curr_pos[0],
                "lon"    : self.mc.curr_pos[1],
                "alt"    : 0,
                "epx"    : 10.000, # longitude error estimated in meters
                "epy"    : 10.000, # latitude error estimate in meters
                "epv"    : 0,      # estimated vertical error in meters
                "track"  : 0.0000,
                "speed"  : 0.000,
                "climb"  : 0.000,
                "eps"    : 0.00,   # speed error estimated in meters/second
            })

    def get_cmd_DEVICES(self):
        return "%s\r\n" % json.dumps({
                "class"     : "DEVICES",
                "devices"   :
                    [
                        { "class"     : "DEVICE",
                          "path"      : self.device,
                          "activated" : self.get_time(self.time_started),
                          "flags"     : 1,
                          "driver"    : "Generic NMEA",
                          "native"    : 0,
                          "bps"       : 57600,
                          "parity"    : "N",
                          "stopbits"  : 1,
                          "cycle"     : 1.00 }
                    ],
            })

    def get_cmd_WATCH(self, params):
        return self.get_cmd_DEVICES() \
             + "%s\r\n" % json.dumps({
               "class"  : "WATCH",
               "enable" : True,
               "json"   : True,
               "nmea"   : False,
               "raw"    : 0,
               "scaled" : False,
               "timing" : False,
           })

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        logging.info("Listening on port %d" % self.port)

        read_list = [server_socket]
        write_list = []
        while not self.quit:
            readable, writable, errored = select.select(read_list, [], [], 1)
            if len(readable) > 0:
                for s in readable:
                    if s is server_socket:
                        client_socket, address = server_socket.accept()
                        read_list.append(client_socket)
                        logging.info("Connection from %s" % str(address))
                        client_socket.send(self.get_cmd_VERSION({}))
                    else:
                        data = s.recv(4096)
                        data
                        if data:
                            # remove line terminators
                            if data[-1] == '\n': data = data[0:-1]
                            if data[-1] == '\r': data = data[0:-1]

                            # parse line
                            command, i, params = data.partition("=")
                            if command[0] != "?":
                                logging.error("received trash [%s]" % data)
                                continue
                            command = command[1:]
                            if i is not None: # no params
                                if params[-1] == ';':
                                    params = params[0:-1]
                                logging.info("%s = %s" % (command, json.dumps(params, indent = 4)))
                                params = json.loads(params)
                            else:
                                params = { }

                            # process command
                            if command == "VERSION":
                                s.send(self.get_cmd_VERSION(params))
                            elif command == "WATCH":
                                s.send(self.get_cmd_WATCH(params))
                                write_list.append(client_socket)
                            else:
                                logging.error("UNKNOWN COMMAND [%s]" % data)
                                s.send(
                                    json.dumps({
                                        "class":   "ERROR",
                                        "message": "Unrecognized request '%s'" % command}) + "\r\n")
                        else:
                            logging.info("Closed gpsd connection.")
                            s.close()
                            read_list.remove(s)
                            if s in write_list:
                                write_list.remove(s)
            else:
                if self.mc.curr_pos is not None:
                    for s in write_list:
                        s.send(self.get_cmd_GST() + self.get_cmd_TPV())

