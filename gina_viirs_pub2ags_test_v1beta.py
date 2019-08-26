#! /usr/bin/env python3

print ("Hello Python3")

import arcpy
print ("imported arcpy")

import os
print ("imported os")

import sys
print ("imported sys")

import pandas
print ("imported pandas")

from datetime import date, datetime
print ("imported date & datetime from datetime")

import urllib
print ("imported urllib")

import urllib3
print ("imported urllib3")

import requests
print ("imported requests")

#import urllib2
#print ("imported urllib2")

# gen tgturllist
tgturllist = []

# set target directories
viirs_truecolor = "/mnt/rear-drives/gis/afs_fire_heat/tif/truecolor/"
print ("viirs_truecolor dir set to: " + viirs_truecolor)
viirs_firecolor = "/mnt/rear-drives/gis/afs_fire_heat/tif/firecolor/"
print ("viirs_firecolor dir set to: " + viirs_firecolor)
viirs_firetemp = "/mnt/rear-drives/gis/afs_fire_heat/tif/firetemp/"
print ("viirs_firetemp dir set to: " + viirs_firetemp)

# functions
def dwnldFirecolor(fireurl, firefile):
    os.chdir(viirs_firecolor)
    urllib.request.urlretrieve(fireurl, firefile)
    print ("Downloading "+ firefile + " to " + viirs_firecolor)
    return firefile

def dwnldFiretemp(firetempurl, firetempfile):
    os.chdir(viirs_firetemp)
    urllib.request.urlretrieve(firetempurl, firetempfile)
    print ("Downloading "+ firetempfile + " to " + viirs_firetemp)
    return firetempfile

def dwnldTruecolor(trueurl, truefile):
    os.chdir(viirs_truecolor)
    urllib.request.urlretrieve(trueurl, truefile)
    print ("Downloading "+ truefile + " to " + viirs_truecolor)
    return truefile

# slurp url for images
url = "http://nrt-ops.gina.alaska.edu/products.txt?action=index&commit=Get+Products&controller=products&end_date=&processing_levels%5B%5D=geotiff_l2&start_date=&utf8=%E2%9C%93"
sock = requests.get(url) 
#sockstr = sock.read.decode()
#for I in sockstr:
#    tgturl = I.rstrip()
#    tgturllist += tgturl
stack = sock.text
#print (stack)
tgturllist = stack.split("\n")
#print (tgturllist)

### parse urls for tgturl, tgtfile, tgtdate, tgttime, tgtsource, and tgtdesc ###
urldictlist = []
for tgturl in tgturllist:
    if len(tgturl) <= 1:
        continue
    tmpdict = {}
    tmpdict["tgturl"] = tgturl
    tgtfile = os.path.basename(tgturl)
    if len(tgtfile.split(".")) <= 1:
        continue
    tmpdict["tgtfile"] = tgtfile
    tgtsource = tgtfile.split(".")[0]
    if tgtsource == "npp" or tgtsource == "noaa20":
        tmpdict["tgtsource"] = tgtfile.split(".")[0]
    else:
        continue
    tmpdict["tgtsource"] = tgtsource
    desc = tgtfile.split("_")[-1]
    if desc == "i01.tif":
        tgtdesc = "firecolor"
    elif desc == "m10.tif":
        tgtdesc = "firetemp"
    elif desc == "color.tif":
        tgtdesc = "truecolor"
    else:
        continue
    tmpdict["tgtdesc"] = tgtdesc
    tgtdate = tgtfile.split(".")[1]
    tgttime = tgtfile.split(".")[2].split("_")[0]
    tgtdatetime = datetime.strptime(tgtdate + tgttime, "%Y%m%d%H%M")
    tmpdict["tgtdatetime"] = tgtdatetime
    urldictlist.append(tmpdict)

### data frame time ###
urlpddataframe = pandas.DataFrame(urldictlist)
urldataframesorted = urlpddataframe.sort_values(by =['tgtdatetime', 'tgtdesc'], ascending =[False, True])
#print (urldataframesorted)

## get most recent dataframe records ###
mostRecentFirecolor = urldataframesorted.iloc[0]
#print ("mostRecentFirecolor: " + str(mostRecentFirecolor))
mostRecentFiretemp = urldataframesorted.iloc[1]
#print ("mostRecentFiretemp: " + str(mostRecentFiretemp))
mostRecentTruecolor = urldataframesorted.iloc[2]
#print ("mostRecentTruecolor: " + str(mostRecentTruecolor))

### mostRecent<desc> Indices
# 0: tgtdate
# 1: tgtdesc
# 2: tgtfile
# 3: tgtsource
# 4: tgturl

##### list existing files in downlaod directories and check dates and times ###
# firecolor
existingFirecolorFile = ""
firecolorDirContents = os.listdir(viirs_firecolor)
if firecolorDirContents:
    for existingFirecolorFile in firecolorDirContents:
        existingFirecolorDate = existingFirecolorFile.split(".")[1]
        existingFirecolorTime = existingFirecolorFile.split(".")[2].split("_")[0]
        existingFirecolorDateTime = datetime.strptime(existingFirecolorDate + existingFirecolorTime, "%Y%m%d%H%M")
        # compare tgtdate and tgttime against existing date and existing time
        if mostRecentFirecolor[0] > existingFirecolorDateTime:
            print ("file " + mostRecentFirecolor[2] + " is more recent than " + existingFirecolorFile)
            print ("removing " + viirs_firecolor + "/" + existingFirecolorFile)
            os.remove(viirs_firecolor + "/" + existingFirecolorFile)
            existingFirecolorFile = dwnldFirecolor(mostRecentFirecolor[4], mostRecentFirecolor[2])
        else:
            print ("Most recent firecolor file already exists!")
            exit
else:
    existingFirecolorFile = dwnldFirecolor(mostRecentFirecolor[4], mostRecentFirecolor[2])


# firetemp
existingFiretempFile = ""
firetempDirContents = os.listdir(viirs_firetemp)
if firetempDirContents:
    for existingFiretempFile in firetempDirContents:
        existingFiretempDate = existingFiretempFile.split(".")[1]
        existingFiretempTime = existingFiretempFile.split(".")[2].split("_")[0]
        existingFiretempDateTime = datetime.strptime(existingFiretempDate + existingFiretempTime, "%Y%m%d%H%M")
        # compare tgtdate and tgttime against existing date and existing time
        if mostRecentFiretemp[0] > existingFiretempDateTime:
            print ("file " + mostRecentFiretemp[2] + " is more recent than " + existingFiretempFile)
            print ("removing " + viirs_firetemp + "/" + existingFiretempFile)
            os.remove(viirs_firetemp + "/" + existingFiretempFile)
            existingFiretempFile = dwnldFiretemp(mostRecentFiretemp[4], mostRecentFiretemp[2])
        else:
            print ("Most recent firetemperature file already exists!")
            exit
else:
    existingFiretempFile = dwnldFiretemp(mostRecentFiretemp[4], mostRecentFiretemp[2])

# truecolor
existingTruecolorFile = ""
truecolorDirContents = os.listdir(viirs_truecolor)
if truecolorDirContents:
    for existingTruecolorFile in truecolorDirContents:
        existingTruecolorDate = existingTruecolorFile.split(".")[1]
        existingTruecolorTime = existingTruecolorFile.split(".")[2].split("_")[0]
        existingTruecolorDateTime = datetime.strptime(existingTruecolorDate + existingTruecolorTime, "%Y%m%d%H%M")
        if mostRecentTruecolor[0] > existingTruecolorDateTime:
            print ("file " + mostRecentTruecolor[2] + " is more recent than " + existingTruecolorFile)
            print ("removing " + viirs_truecolor + "/" + existingTruecolorFile)
            os.remove(viirs_truecolor + "/" + existingTruecolorFile)
            existingTruecolorFile = dwnldTruecolor(mostRecentTruecolor[4], mostRecentTruecolor[2])
        else:
            print ("Most recent truecolor file already exists!")
            exit()
else:
    existingTruecolorFile = dwnldTruecolor(mostRecentTruecolor[4], mostRecentTruecolor[2])


#######  ArcGIS Server - Publish Image Services  #######

# a few more variables that ags will use
firecolorname = "Most_Recent_GINA_VIIRS_FireColor"
firetempname = "Most_Recent_GINA_VIIRS_FireTemperature"
truecolorname = "Most_Recent_GINA_VIIRS_Truecolor"
firecolorsddraft = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/sddraft/firecolor.sddraft"
firetempsddraft = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/sddraft/firetemp.sddraft"
truecolorsddraft = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/sddraft/truecolor.sddraft"
firecolorsd = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/sd/firecolor.sd"
firetempsd = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/sd/firetemp.sd"
truecolorsd = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/sd/truecolor.sd"
ags = "/mnt/rear-drives/gis/afs_fire_heat/ags_files/ags/mynock_ags_admin.ags"

firecolorFilePath = viirs_firecolor + existingFirecolorFile
#print (firecolorFilePath)
firetempFilePath = viirs_firetemp + existingFiretempFile
#print (firetempFilePath)
truecolorFilePath = viirs_truecolor + existingTruecolorFile
#print (trucolorFilePath)


### generate and publish service definitions ###

## publish firecolor service
try:
    print ("Generatating Firecolor SD draft")
    arcpy.CreateImageSDDraft(firecolorFilePath, firecolorsddraft, firecolorname, 'FROM_CONNECTION_FILE', ags, True, "afs", "GINA NRT Firecolor","GINA,NRT,Firecolor")
except:
    print (arcpy.GetMessages()+ "\n\n")
    sys.exit("Failed in generating Firecolor SD draft")

### analyze firecolor service definition draft
# analyzefirecolorsddraft = arcpy.mapping.AnalyzeForSD(firecolorsddraft)
#print ("The following information was returned during analysis of the image service: " + firecolorname)
#for key in ('messages', 'warnings', 'errors'):
#  print ('----' + key.upper() + '---')
#  vars = analyzefirecolorsddraft[key]
#  for ((message, code), layerlist) in vars.iteritems():
#    print ('    ', message, ' (CODE %i)' % code)
#    print ('       applies to:',)
#    for layer in layerlist:
#        print (layer.name,)
#    print ()

# if the firecolor sddraft analysis does not contain errors, stage and upload the service definition
if firecolorsddraft: #analyzefirecolorsddraft['errors'] == {}:
    try:
        try:
            os.remove(firecolorsd)
        except:
            pass
        print ("Staging service to create service definition")
        arcpy.StageService_server(firecolorsddraft, firecolorsd)

        print ("Uploading the service definition and publishing image service")
        arcpy.UploadServiceDefinition_server(firecolorsd, ags)

        print (firecolorname + " service successfully published")
    except:
        print (arcpy.GetMessages()+ "\n\n")
        sys.exit("Failed to stage and upload service")
else:
    print (firecolorname + " service could not be published because errors were found during analysis.")
    print (arcpy.GetMessages())


## publish firetemp service
try:
    print ("Generatating FireTemperature SD draft")
    arcpy.CreateImageSDDraft(firetempFilePath, firetempsddraft, firetempname, 'FROM_CONNECTION_FILE', ags, True, "afs", "GINA NRT VIIRS FireTempeature","GINA,NRT,VIIRS,FireTemperature")
except:
    print (arcpy.GetMessages()+ "\n\n")
    sys.exit("Failed in generating Firetemp SD draft")

### analyze firetemp service definition draft
#analyzefiretempsddraft = arcpy.mapping.AnalyzeForSD(firetempsddraft)
#print ("The following information was returned during analysis of the image service: " + firetempname)
#for key in ('messages', 'warnings', 'errors'):
#  print ('----' + key.upper() + '---')
#  vars = analyzefiretempsddraft[key]
#  for ((message, code), layerlist) in vars.iteritems():
#    print ('    ', message, ' (CODE %i)' % code)
#    print ('       applies to:',)
#    for layer in layerlist:
#        print (layer.name,)
#    print ()

# if the firetemp sddraft analysis does not contain errors, stage and upload the service definition
if firetempsddraft:  #['errors'] == {}:
    try:
        try:
            os.remove(firetempsd)
        except:
            pass
        print ("Staging service to create service definition")
        arcpy.StageService_server(firetempsddraft, firetempsd)

        print ("Uploading the service definition and publishing image service")
        arcpy.UploadServiceDefinition_server(firetempsd, ags)

        print (firetempname + " service successfully published")
    except:
        print (arcpy.GetMessages()+ "\n\n")
        sys.exit("Failed to stage and upload service")
else:
    print (firetempname + " service could not be published because errors were found during analysis.")
    print (arcpy.GetMessages())


## publish truecolor service
try:
    print ("Generatating Truecolor SD draft")
    arcpy.CreateImageSDDraft(truecolorFilePath, truecolorsddraft, truecolorname, 'FROM_CONNECTION_FILE', ags, True, "afs", "GINA NRT Truecolor","GINA,NRT,Truecolor")
except:
    print (arcpy.GetMessages()+ "\n\n")
    sys.exit("Failed in generating Truecolor SD draft")

### analyze truecolor service definition draft
#analyzetruecolorsddraft = arcpy.mapping.AnalyzeForSD(truecolorsddraft)
#print ("The following information was returned during analysis of the image service: " + truecolorname)
#for key in ('messages', 'warnings', 'errors'):
#  print ('----' + key.upper() + '---')
#  vars = analyzetruecolorsddraft[key]
#  for ((message, code), layerlist) in vars.iteritems():
#    print ('    ', message, ' (CODE %i)' % code)
#    print ('       applies to:',)
#    for layer in layerlist:
#        print (layer.name,)
#    print ()

# if the truecolor sddraft analysis does not contain errors, stage and upload the service definition
if truecolorsddraft:  #['errors'] == {}:
    try:
        try:
            os.remove(truecolorsd)
        except:
            pass
        print ("Staging service to create service definition")
        arcpy.StageService_server(truecolorsddraft, truecolorsd)

        print ("Uploading the service definition and publishing image service")
        arcpy.UploadServiceDefinition_server(truecolorsd, ags)

        print (truecolorname + " service successfully published")
    except:
        print (arcpy.GetMessages()+ "\n\n")
        sys.exit("Failed to stage and upload service")
else:
    print (truecolorname + " service could not be published because errors were found during analysis.")
    print (arcpy.GetMessages())


exit ()










