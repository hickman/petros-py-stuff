#! /usr/bin/env python3

print("Hello Python3")
import arcpy
from arcpy import env
import os
import sys
from datetime import date, datetime
import csv

# Get sourceFile 
#sourceDir = "txt/viirs_i/"
#sourceFile = os.listdir(sourceDir)
inFile = sys.argv[1]
print('Processing ' + inFile)
outDir = "csv/"

# Process source txt file
headerRow = 'LAT,LON,OBS,PROC,SRC,CONF,TEMPK,TEMPF,RADMW,FILE' + '\n'
#for inFile in sourceFile:
sFilename = os.path.basename(inFile).split('.')[0]
outFile = open(os.path.join(outDir, sFilename + '.csv'), 'w')
outFile.write(headerRow)
parsedFilename = sFilename.split('_')
obsd = parsedFilename[2].lstrip('d')
obsst = parsedFilename[3].lstrip('t')
obset = parsedFilename[4].lstrip('e')
procd = parsedFilename[6].lstrip('c').rstrip('00')
obsdatetime = datetime.strptime(obsd + obset, "%Y%m%d%H%M%f")
procdatetime = datetime.strptime(procd, "%Y%m%d%H%M%f")
src = parsedFilename[1]
with open(os.path.join(inFile), newline='') as f:
    reader = csv.reader(f)
    for column in reader:
        lat = column[0]
        lon = column[1]
        tempk = column[2]
        tempf = round((float(tempk)*(9/5))-459.67, 1) #https://www.rapidtables.com/convert/temperature/how-kelvin-to-fahrenheit.html
        conf = column[5]
        if conf == '7':
            conftxt = "Low confidence"
        elif conf == '8':
            conftxt = "Nominal confidence"
        elif conf == '9':
            conftxt = "High confidence"
        rmw = column[6]
        row = lat + "," + lon + "," + str(obsdatetime) + "," + str(procdatetime) + ",GINA-" + src + "," + conftxt + "," +  tempk + "," + str(tempf) + "," + rmw + "," + sFilename + '\n'
        outFile.write(row)
    f.close
outFile.close

## Generate XY Event Layer 
arcpy.env.overwriteOutput = True
aprxPub = arcpy.mp.ArcGISProject("aprx/fire_heat_points_service.aprx")
mPub = aprxPub.listMaps("Map")[0]

incsv = "csv/" + os.listdir(outDir)[0]
x = 'LON'
y = 'LAT'
srs = arcpy.SpatialReference(4326)
lyrname = 'fire_heat_points_service_update'
arcpy.MakeXYEventLayer_management(incsv, x, y, lyrname, srs)
arcpy.SaveToLayerFile_management(lyrname, "lyrx/fire_heat_points_service_update.lyrx", 'RELATIVE')
lyrx = arcpy.mp.LayerFile("lyrx/fire_heat_points_service_update.lyrx")
mPub.addLayer(lyrx)
aprxPub.save()

#ags_dev = "ags/stage0.gina.alaska.edu.ags"
#ags_prod = "ags_files/ags/pedro.fire.gina.alaska.edu.ags"
#
#
#sddraftDir = "ags_files/sddraft/"
#sddraftFile = "fire_heat_points_service_update.sddraft"
#sddraftPath = os.path.join(sddraftDir, sddraftFile)
#sddraft = arcpy.sharing.CreateSharingDraft('STANDALONE_SERVER', 'MAP_SERVICE', lyrname, mPub)
#sddraft.targetServer = ags_prod
#sddraft.exportToSDDraft(sddraftPath)
#
#sdDir = "ags_files/sd/"
#sdFile = "fire_heat_points_service_update.sd"
#sdPath = os.path.join(sdDir, sdFile)
#print(sdPath)
#arcpy.StageService_server(sddraftPath, sdPath)
#arcpy.UploadServiceDefinition_server(sdPath, ags_prod, in_folder_type='EXISTING', in_folder='afs')
#
## Clean up
#mPub.removeLayer(mPub.listLayers('fire_heat_points_service_update')[0])
#aprxPub.save()
#rmLyrx = "lyrx/fire_heat_points_service_update.lyrx"
#os.remove(rmLyrx)
#os.remove(sddraftPath)
#os.remove(sdPath)


# All done
print("All done")
exit()

