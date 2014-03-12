gpsmap
======

This is a GPSD (http://gpsd.berlios.de/) simulator using a map.

This tool is designed for making possible to use Kismet (and other GPSD based
tools) inside buildings, zones without GPS signal, or even without a GPS
device.

The inner working is simple: you only have to set three reference coordinate
points on the map using this tool, and the integrated GPSD emulator will start
to send your position coordinates throught the localhost:2947 port.

This program can also save a planned route and replay it automatically at a
certain speed (walk speed parameter).

Screenshot:
![gpsmap screenshot](/doc/gpsmap-screenshot.jpg "gpsmap screenshot")

Quick start
-----------

You will need Python and pyGTK libraries.

This program is written for Linux, but it should be work seamlessly on other
UNIX platform. Due it uses sockets it may not work correctly on Windows.

To start the program run:

  python ./gpsmap

To start a new project follow these steps:

1. Load your image map (JPG, PNG, ...) using the "Config -> Load map image"
   menu option.

2. Go to the "Config -> Reference points -> Set reference A". A yellow-cross
   following your mouse will apear on your map.

   Choose your reference base point (we call it Reference A) and click on it.
   A dialog will appear asking for the geographic coordinates for this point.
   Use some earth map software (like Google Earth) to find them.

   ![gpsmap screenshot](/doc/choose-ref-A-01.jpg "choosing reference point A")

   Once confirmed you will get the following mark on your map:

   ![gpsmap screenshot](/doc/choose-ref-A-02.jpg "Reference point A set")

3. You will need to do this operation two times more. Now we will set the
   horizontal axis reference point (we call it H).
   
   Go to the "Config -> Reference points -> Set reference H". This time you
   will get a yellow line with a little cross moving along it. This cross
   will set the position of the H point when you click with your mouse.

   Once you clicked it will appear a dialog asking for the geographical
   coordinates of this point.

   ![gpsmap screenshot](/doc/choose-ref-H-01.jpg "choosing reference point H")

   Once confirmed you will get the following mark on your map:

   ![gpsmap screenshot](/doc/choose-ref-H-02.jpg "Reference point H set")

4. Repeat this process, but this time with the verical axis setting the
   vertical axis reference point (we call it V).

   ![gpsmap screenshot](/doc/choose-ref-V-01.jpg "choosing reference point V")

   Again you will get a mark on your map:

   ![gpsmap screenshot](/doc/choose-ref-V-02.jpg "Reference point V set")

5. Now gpsmap is fully configured. You can test that it works using the ruler
pressing and dragging the mouse right-button over the map:

   ![gpsmap screenshot](/doc/ruler.jpg "Ruler")

Or testing the precision of your routes saving them with the "File -> Save KML
route" option and loading them in Google Earth maps. If you have set correctly
the three reference points your route will fit perfectly on the Google Earth
maps!

   ![gpsmap screenshot](/doc/route-kml.jpg "KML route on Google Earth")

Tracing a route
---------------

For tracing a route you only have to press the mouse middle-button. Each time
you press this button you will add a new route point:

![gpsmap screenshot](/doc/route.jpg "Adding route points")

Please note that if you have running a software that listens to the GPSD port,
it will receive the coordinates of the point you a pressing. You will know
which coordinates are being sent throught the GPSD port looking for a pulsating
circle in your map:

![gpsmap screenshot](/doc/gps-position.jpg "GPS position")

Playing a route
---------------

For playing a route press the "Animate -> Start" option menu. It will start
playing the route while you are moving with your laptop at the same speed:

![gpsmap screenshot](/doc/walking.jpg "Walking a route")

You can configure your walking speed in the "Config -> Set walking speed":

![gpsmap screenshot](/doc/walking-speed.jpg "Walking speed")

Please note that if the "Animate -> Pause at checkpoints" option is checked,
the route will pause automatically each time you reach a control point:

![gpsmap screenshot](/doc/walking-pause-checkpoint.jpg "Pause at checkpoint")

You can resume the route hitting the ENTER key. The "Pause at checkpoints"
option is useful for resynchronizing your walking with the gpsmap walking :D

Please note that the ENTER key is a "PAUSE/RESUME" key binding.
