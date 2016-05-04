from __future__ import print_function
from fractions import Fraction
import os
points = []
coordinates = []
raspberries = []
width = 6
height = 30
offset = 10

initial_lat = -10062973.096
initial_long = 4675266.934

# rPI_145 is 2.794 meters (x) and 0.5461 meters (y) from the initial lat/long point
rPI_145_lat = initial_lat + 2.794
rPI_145_long = initial_long + 0.5461
rPI_145 = QgsPoint(rPI_145_lat, rPI_145_long)
points.append(rPI_145)

# rPIs are separated by rPI_x in meters
rPI_x = 0.9779
# rPIs are separated by rPI_y in meters
rPI_y = 0.4572

# Deriving initial rPI coordinates.
rPI_11_lat = rPI_145_lat - (rPI_x * 2)
rPI_11_long = rPI_145_long + (rPI_y * 22)
rPI_11 = QgsPoint(rPI_11_lat, rPI_11_long)
points.append(rPI_11)
coordinates.append([rPI_11_lat, rPI_11_long])
raspberries.append("10.9.0.11")
init_x = (abs(11-(width*height)-offset) % width) + 1
init_y = (abs(11-(width*height)-offset) / width) + 1

prev_x = init_x
prev_y = init_y
prev_lat = rPI_11_lat
prev_long = rPI_11_long

for ind in range(12, 191):
    formula = abs(ind-(width*height)-offset)
    y = (formula / width) + 1
    x = (formula % width) + 1
    # Calculating latitude longitude changes via grid coords
    if x < prev_x:
        rPI_lat = prev_lat + (rPI_x * (prev_x - x))
    elif x > prev_x:
        rPI_lat = prev_lat - (rPI_x * (x - prev_x))
    else:
        rPI_lat = prev_lat
    # Doing the same for y / longitude
    if y < prev_y:
        rPI_long = prev_long - (rPI_y * (prev_y - y))
    elif y > prev_y:
        rPI_long = prev_long + (rPI_y * (y - prev_y))
    else:
        rPI_long = prev_long
    rPI_point = QgsPoint(rPI_lat, rPI_long)
    rPI_coords = [rPI_lat, rPI_long]
    points.append(rPI_point)
    coordinates.append(rPI_coords)
    raspberries.append("10.9.0."+str(ind))
    prev_x = x
    prev_y = y
    prev_lat = rPI_lat
    prev_long = rPI_long

# create a memory layer with all the rPI points
layer = QgsVectorLayer('Point', 'points', 'memory')
# add the first point (initial point)
pr = layer.dataProvider()
pt = QgsFeature()
point1 = QgsPoint(initial_lat, initial_long)
pt.setGeometry(QgsGeometry.fromPoint(point1))
pr.addFeatures([pt])
layer.updateExtents()
# For loop for the points
for rPI in points:
    pr = layer.dataProvider()
    pt = QgsFeature()
    pt.setGeometry(QgsGeometry.fromPoint(rPI))
    pr.addFeatures([pt])
    layer.updateExtents()
# add the layer to the canvas

QgsMapLayerRegistry.instance().addMapLayers([layer])

# Converting points from meter coordinates (3857) to GPS / Lat & Long coordinates in WGS 4326
# ESRI:3857 WGS Pseudo-Mercator
sourceCrs = QgsCoordinateReferenceSystem(3857)
# ESRI:4326 WGS (GCS)
destCrs = QgsCoordinateReferenceSystem(4326)
# Setting up transformation vector
xform = QgsCoordinateTransform(sourceCrs, destCrs)

transformed = []
for rPI in points:
    transformed.append(xform.transform(rPI))

transformed_coords = []
for rPI_c in coordinates:
    transformed_coords.append(xform.transform(QgsPoint(rPI_c[0], rPI_c[1])))

os.chdir("D:\\DDPSC\\Raspberry_Pi\\GIS\\")
filename_1 = "transformed_coords.txt"
filename_2 = "jpeg_exif_coords.txt"
with open(filename_1, 'w') as fn_1:
    with open(filename_2, 'w') as fn_2:
        for index in range(len(transformed_coords)):
            trans = transformed_coords[index]
            lat = trans[0]
            lng = trans[1]
            print("{0} {1} {2}".format(raspberries[index], lat, lng), file=fn_1)
            if lat < 1:
                lat = abs(lat)
                lat_ref = "W"
                lat = Fraction(lat)
            else:
                lat = abs(lat)
                lat_ref = "E"
                lat = Fraction(lat)
            if lng < 1:
                lng = abs(lng)
                lng_ref = "S"
                lng = Fraction(lng)
            else:
                lng = abs(lng)
                lng_ref = "N"
                lng = Fraction(lng)
            print("{IP} {lng_ref}; {lng},0/1,0/1; {lat_ref}; {lat},0/1,0/1; 0; 604/1; 2".format(IP=raspberries[index], lng_ref=lng_ref, lng=lng, lat_ref=lat_ref, lat=lat), file=fn_2)