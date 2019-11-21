#! /usr/bin/env python3

import arcpy
from arcpy import env
import os
import sys
from datetime import date, datetime
import pytz
import csv


# Get sourceFile
# Sample sourcFile = r"E:\gina\afs\txt\viirs_i\FireLoc375_npp_d20190709_t1220444_e1233325_b00001_c20190709130340986000_ipop_dev.txt"

#### Need to add logic to filter for txt only and run two loops 1) for jpss/viirs/level2 and 2) for npp/viirs/level2!!!  #### 
##j01Dir = "R:/auto/gis/gvolipopp/jpss1/viirs/level2/"
##j01List = os.listdir(j01Dir)
##for i, val in enumerate(j01List):
##    val = j01Dir + val
##    j01List[i] = val
##nppDir = "R:/auto/gis/gvolipopp/npp/viirs/level2/"
##nppList = os.listdir(nppDir)
##for i, val in enumerate(nppList):
##    val = nppDir + val
##    nppList[i] = val
##sourceList = [*j01List, *nppList]
##print(j01List)
##print(nppList)
##print(sourceList)

inPath = sys.argv[1]
#inPath = "/home/ags/afs_fire_heat/txt/viirs_i/FireLoc375_npp_d20190820_t2228348_e2241229_b00001_c20190820230929858000_ipop_dev.txt"
tgtTable = "/home/ags/arcgis/server/usr/directories/arcgissystem/arcgisinput/afs/VIIRS_iBand_FireHeatPoints.MapServer/extracted/v101/viirs_iband_fireheatpoints.gdb/iband_fire_heat_xy_points"
fields = ['LATITUDE', 'LONGITUDE', 'OBSERVEDTIME', 'PROCESSEDTIME', 'SOURCE', 'CONFIDENCE', 'TEMPKELVIN', 'TEMPFAHRENHEIT', 'RADMW', 'FILE']
cursor = arcpy.da.InsertCursor(tgtTable, fields)

# Process source txt files
inFile = os.path.basename(inPath)
if inFile.split(".")[-1] == "txt" and inFile.split("_")[0] == "FireLoc375":
    print('Processing ' + inFile)
    sFilename = inFile.split('.')[0]
    parsedFilename = sFilename.split('_')
    obsd = parsedFilename[2].lstrip('d')
    obsst = parsedFilename[3].lstrip('t')  #correct UTC to AKDT
    obset = parsedFilename[4].lstrip('e')  #correct UTC to AKDT
    procd = parsedFilename[6].lstrip('c').rstrip('00') #correct UTC to AKDT
    utcobsdatetime = datetime.strptime(obsd + obsst, "%Y%m%d%H%M%f")
    utcprocdatetime = datetime.strptime(procd, "%Y%m%d%H%M%f")  #"%Y%m%d%H%M%f" #"%m/%d/%Y/%H%M%f"
    aktz = pytz.timezone('America/Anchorage')
    aktobsdatetime = utcobsdatetime.replace(tzinfo=pytz.utc).astimezone(aktz)
    aktprocdatetime = utcprocdatetime.replace(tzinfo=pytz.utc).astimezone(aktz)
    src = parsedFilename[1]
    with open(inPath, newline='') as f:
        reader = csv.reader(f)
        for column in reader:
            lat = column[0]
            lon = column[1]
            tempk = column[2]
            tempf = round((float(tempk)*(9/5))-459.67, 1) #https://www.rapidtables.com/convert/temperature/how-kelvin-to-fahrenheit.html
            conf = column[5]
            if conf == '7':
                conftxt = "Low confidence fire pixel"
            elif conf == '8':
                conftxt = "Nominal confidence fire pixel"
            elif conf == '9':
                conftxt = "High confidence fire pixel"
            rmw = column[6]
            row = [lat, lon, aktobsdatetime, aktprocdatetime, "GINA-" + src, conftxt, tempk, tempf, rmw, sFilename]
            cursor.insertRow(row)
        f.close
else:
    exit()

del cursor

# Add XY Events to the map
arcpy.env.overwriteOutput = True
aprxPub = arcpy.mp.ArcGISProject("/home/ags/afs_fire_heat/aprx/fire_heat_points_service.aprx")
mPub = aprxPub.listMaps("Map")[0]

lyrxDir = "/home/ags/afs_fire_heat/lyrx/"
x = 'LONGITUDE'
y = 'LATITUDE'
srs = arcpy.SpatialReference(4326)    
arcpy.MakeXYEventLayer_management(tgtTable, x, y, sFilename, srs)
lyrxName = sFilename + ".lyrx"
lyrxPath = os.path.join(lyrxDir, lyrxName)    
arcpy.SaveToLayerFile_management(sFilename, lyrxPath, 'RELATIVE')
lyrx = arcpy.mp.LayerFile(lyrxPath)
mPub.addLayer(lyrx)
aprxPub.save()

tgtFeatureClass = "/home/ags/arcgis/server/usr/directories/arcgissystem/arcgisinput/afs/VIIRS_iBand_FireHeatPoints.MapServer/extracted/v101/viirs_iband_fireheatpoints.gdb/VIIRS_iBand_FireHeatPoints"
arcpy.Append_management(mPub.listLayers(sFilename)[0], tgtFeatureClass, "NO_TEST")

mPub.removeLayer(mPub.listLayers(sFilename)[0])
aprxPub.save()

arcpy.DeleteRows_management(tgtTable)

print("All done")
exit()

##viirsLayer = "VIIRS_iBand_FireHeatPoints"
##arcpy.env.workspace = "R:/mnt/data/afs/arcgis/server/usr/directories/arcgissystem/arcgisinput/afs/VIIRS_iBand_FireHeatPoints.MapServer/extracted/p20/viirs_iband_fireheatpoints.gdb"
##arcpy.MakeFeatureLayer_management(arcpy.ListFeatureClasses()[0], viirsLayer)
##aprxPub.save()


###ags_dev = "E:/gina/afs/ags/stage0.gina.alaska.edu.ags"
##ags_prod = "E:/gina/afs_fire_heat/ags_files/ags/pedro.fire.gina.alaska.edu.ags"


##sddraftDir = "E:/gina/afs_fire_heat/ags_files/sddraft/"
##sddraftFile = "fire_heat_points_service_update.sddraft"
##sddraftPath = os.path.join(sddraftDir, sddraftFile)
##sddraft = arcpy.sharing.CreateSharingDraft('STANDALONE_SERVER', 'MAP_SERVICE', lyrname, mPub)
##sddraft.targetServer = ags_prod
##sddraft.exportToSDDraft(sddraftPath)
##
##sdDir = "E:/gina/afs_fire_heat/ags_files/sd/"
##sdFile = "fire_heat_points_service_update.sd"
##sdPath = os.path.join(sdDir, sdFile)
##arcpy.StageService_server(sddraftPath, sdPath)
##arcpy.UploadServiceDefinition_server(sdPath, ags_prod, in_folder_type='EXISTING', in_folder='afs')
##
### Clean up
##mPub.removeLayer(mPub.listLayers('fire_heat_points_service_update_win')[0])
##aprxPub.save()
###rmLyrx = "E:/gina/afs_fire_heat/lyrx/fire_heat_points_service_update.lyrx"
###os.remove(rmLyrx)
###os.remove(sddraftPath)
###os.remove(sdPath)


# All done
#exit()

