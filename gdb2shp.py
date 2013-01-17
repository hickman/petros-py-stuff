# converts an esri file geodatabase (gdb) to a dir of shapefiles, geotifs and dbf tables
# maintains the gdb organization using directories in place of gdb datasets.  
# does not convert relationship classes.

### usage:
# must be copied and ran from the same dir as the file geodatabase.
# requires name of input file geodatabase as the first parameter.
# requires the name of the output directory as the second parameter.

import arcpy
import os, sys
from arcpy import env

path = sys.argv[0]
gdb = sys.argv[1]
out = sys.argv[2]

fullin = os.path.dirname(path) + "/"  +  gdb
wrksp = fullin.replace("\\", "/")
print "... converting " + os.path.dirname(path) + "\\" + gdb + " to shapefiles"

#print "making output dir " + os.path.dirname(path) + "\\" + out
fullout = (os.path.dirname(path) + "\\" + out)
print "... output directory " + fullout
os.mkdir(fullout)

env.workspace = wrksp

# list stand-alone feature classes and copy them to the target dir as shapefiles
fl = arcpy.ListFeatureClasses()
for f in fl:
    arcpy.CopyFeatures_management(f, fullout + "/" + f + ".shp")
    print "... copied feature class " + f + " to " + f + ".shp"

# list rasters and copy them to target dir as tif
rl = arcpy.ListRasters()
for r in rl:
    arcpy.CopyRaster_management(r, fullout + "/" + r + ".tif")
    print "... copied raster " + r + " to " + r + ".tif"

# list and copy all stand-alone tables to target dir as dbf
tabl = arcpy.ListTables()
for t in tabl:
    arcpy.CopyRows_management(t, fullout + "/" + t + ".dbf")
    print "... copied table " + t + " to " + t + ".dbf"

# list feature datasets, mkdir for each dataset, then copy participating feature classes into that dir
fds = arcpy.ListDatasets()
for fd in fds:
    os.mkdir(fullout + "/" + fd, 0777)
    env.workspace = wrksp + "/" + fd
    fcl = arcpy.ListFeatureClasses()
    for fc in fcl:
        arcpy.CopyFeatures_management(fc,  fullout + "/" + fd + "/" + fc + ".shp")
        print "... copied feature class " + fd + "/" + fc + " to /" + fd + "/" + fc + ".shp"

print "... !!! Done !!!"
