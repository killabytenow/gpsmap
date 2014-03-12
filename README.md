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

