import time
import json
import sys
import os
import urllib.request


uselatest = True #True = use latest #False = use Snapshot
internet = 20 #Retry internet connection on first json if failing in seconds (Only Full Numbers (Integers))
scriptdir = os.path.dirname(os.path.realpath(sys.argv[0]))
installedver = ""
mmcconfile = scriptdir + "\\mmc-pack.json"
mcverurl = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
print("Downloading Minecraft Json and Reading")
noint = False
internet = internet if internet >= 1 else 1 #Do Not Change
while internet > 0:
    try:
        response = urllib.request.urlopen(mcverurl)
        jsonfile = response.read()
    except:
        noint = True
        internet = internet - 1
        if internet == 0:
            print("No Internet Found \nExiting")
            exit()
        if (internet % 10) == 9:
            print("\nYour Internet Seems To Be Missing, Retrying\nChecking " + str(internet + 1) + " More Times (Every Second Once)")
        time.sleep(1)
    else:
        if noint == True:
            print("\nThe Internet Connection Returned, Continuing\n")
            noint = False
        internet = 0
print("Loding Minecraft Json")
jsondata = json.loads(jsonfile)
print("Extrating Minecraft Versions")
release = jsondata["latest"]["release"]
snapshot = jsondata["latest"]["snapshot"]
if uselatest == True:
    use = release
    print("\nUsing Newest Found Release = " + release)
else:
    use = snapshot
    print("\nUsing Newest Found Snapshot = " + snapshot)
if not os.path.exists(mmcconfile):
    print("MultiMC Json Config Not Pressent\nPlease Copy This File Into The Instance Root\nExiting")
    time.sleep(2)
    exit()
else:
    f = open(mmcconfile)
    try:
        mmcjson = json.load(f)
    except:
        print("MultiMC Json Config Not In A Json Format\nlease Use A Other Instance\nExiting")
        f.close()
        time.sleep(2)
        exit()
    else:
        f.close()
        try:
            mmcvers = mmcjson["components"][1]["version"]
        except:
            try:
                mmcfilech = mmcjson["formatVersion"]
            except:
                print("MultiMC Json Config Not In The Correct Format\nPlease Use A Other Instance\nExiting")
                time.sleep(2)
                exit()
            else:
                if mmcfilech == 1:
                    print("MultiMC Json Config Not In The Correct Format\nEven If The \"formatVersion\" Tag Seems To Suggest Otherwise\nPlease Use A Other Instance\nExiting")
                    time.sleep(2)
                    exit()
                else:
                    print("MultiMC Json Config Probably Not in The Right Verson \nIt is " + mmcfilech + " \nBut It was Made for Verson 1\nPlease Use A Other Instance\nExiting")
                    time.sleep(2)
                    exit()
        else:
            if use == mmcvers:
                print("MultiMC Is Allready On The Newest Version = " + use)
                time.sleep(2)
                exit()
            else:
                mmcjson["components"][1]["version"] = use
                f = open(mmcconfile, 'w')
                json.dump(mmcjson, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
                print("Installed Version = " + mmcvers + "\nUpdated To Version = " + use)






















'''
if not os.path.exists(versionfile):
    f = open(versionfile, "w")
    f.write(installedver)
    print("The Version File Was Deleted Or There Was No Previously Installed Version")
    f.close()
else:
    f = open(versionfile)
    installedver = f.read()
    if installedver == use:
        f.close()
        print("The Newest Version Is Allready Installed \nVersion = " + use + "\nExiting")
        exit()
    else:
        if installedver == "":
            print("There Was No Previously Installed Version")
        else:
            print("The Installed Version Is = " + installedver)
        f.close()

print("Downloading Version = " + use)
for i in jsondata["versions"]:
    if i["id"] == use:
        break
verjarurl = i["url"]
print("URL for Version json is = " + verjarurl + "\nDownloading Minecraft Jar Json And Reading")
while internetjar > 0:
    try:
        jarsponse = urllib.request.urlopen(verjarurl)
        jsonjarfile = jarsponse.read()
    except:
        noint = True
        internetjar = internetjar - 1
        if internetjar == 0:
            print("No Internet Found \nExiting")
            f = open(versionfile, "w")
            f.write(installedver)
            f.close()
            exit()
        if (internetjar % 10) == 9:
            print("\nYour Internet Seems To Be Missing, Retrying\nChecking " + str(internetjar + 1) + " More Times (Every Second Once)")
        time.sleep(1)
    else:
        if noint == True:
            print("\nThe Internet Connection Returned, Continuing\n")
            noint = False
        internetjar = 0
print("Loding Minecraft Jar Json")
jsonjardata = json.loads(jsonjarfile)
print("Extrating Minecraft Jar URL")
jarurl = jsonjardata["downloads"]["client"]["url"] if useclient == True else jsonjardata["downloads"]["server"]["url"]
print("Using = " + jarurl)
'''
