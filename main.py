# -------------------------------
# Name: GoPro Timelapse
# Version: 1.0.0
#
# Author: Kyle Warner
# Email: kyle@kyleinprogress.com
# -------------------------------

# Imports
import configparser
import datetime
import os
import re
import requests

from datetime import datetime
from dateutil import tz
from time import sleep

# Setup Values
# --------------------------------

defineLatitude = "32.9712"
defineLongitude = "-96.4493"
timezone = "American/Chicago"

from_zone = tz.gettz('UTC')
to_zone = tz.gettz(timezone)

# Current Date & Time
currentDateTime = datetime.now()

currentDate = currentDateTime.strftime("%Y-%m-%d")
currentTime = int(currentDateTime.strftime("%H%M"))

currentYear = datetime.strptime(currentDate, '%Y-%m-%d').year
currentMonth = datetime.strptime(currentDate, '%Y-%m-%d').month
currentDay = datetime.strptime(currentDate, '%Y-%m-%d').day


# Functions
# -------------------------------

def getVarFromFile(filename):
    f = open(filename)
    global data
    data = importlib.load_source('data', '', f)
    f.close()

def imagePath(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Download File
def downloadImg(url):
    imagePath("photos/" + currentDate)
    file_name = "photos/" + currentDate + "/" + str(currentTime) + ".JPG"
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

# Delete File
def deleteImg(img):
    requests.get('http://10.5.5.9/gp/gpControl/command/storage/delete?p=/100GOPRO/' + img)




# Get Sunrise/Sunset for changing camera settings
# -------------------------------
if os.path.isfile('timevalues.ini'):
    config = configparser.ConfigParser()
    config.read("timevalues.ini")

    localSunrise = int(config.get("Times", "Sunrise"))
    localSunset = int(config.get("Times", "Sunset"))
    localMorning = int(config.get("Times", "Morning"))
    localNight = int(config.get("Times", "Night"))

    print("Read Values From Timevalues.ini")


else:
    url = "http://api.sunrise-sunset.org/json?lat=" + defineLatitude + "&lng=" + defineLongitude + "&date=" + currentDate
    r = requests.get(url)
    timestring = r.json()

    utcSunrise = datetime.strptime(timestring["results"]["sunrise"], '%I:%M:%S %p')
    utcSunset = datetime.strptime(timestring["results"]["sunset"], '%I:%M:%S %p')
    utcMorning = datetime.strptime(timestring["results"]["civil_twilight_begin"], '%I:%M:%S %p')
    utcNight = datetime.strptime(timestring["results"]["civil_twilight_end"], '%I:%M:%S %p')

    utcSunrise = utcSunrise.replace(year=currentYear, month=currentMonth, day=currentDay, tzinfo=from_zone)
    utcSunset = utcSunset.replace(year=currentYear, month=currentMonth, day=currentDay, tzinfo=from_zone)
    utcMorning = utcMorning.replace(year=currentYear, month=currentMonth, day=currentDay, tzinfo=from_zone)
    utcNight = utcNight.replace(year=currentYear, month=currentMonth, day=currentDay, tzinfo=from_zone)

    localSunrise = int(utcSunrise.astimezone(to_zone).strftime("%H%M"))
    localSunset = int(utcSunset.astimezone(to_zone).strftime("%H%M"))
    localMorning = int(utcMorning.astimezone(to_zone).strftime("%H%M"))
    localNight = int(utcNight.astimezone(to_zone).strftime("%H%M"))

    import configparser
    config = configparser.ConfigParser()
    config['Times'] = {
        'Sunrise': localSunrise,
        'Sunset': localSunset,
        'Morning': localMorning,
        'Night': localNight }
    with open('timevalues.ini', 'w') as configfile:
        config.write(configfile)

    print("New Timevalues.ini Creates")


# Get Camera Settings / Status
# -------------------------------
r = requests.get('http://10.5.5.9/gp/gpControl/status')
settings = r.json()

# Set Day/Night Settings Based on Time
if localMorning <= currentTime <= localNight:
    if settings["settings"]["69"] != 0:
        requests.get('http://10.5.5.9/gp/gpControl/command/sub_mode?mode=1&sub_mode=0')
        print('Camera set to Single Daylight Mode')
        sleep(1)

    if settings["settings"]["22"] != 0:
        requests.get('http://10.5.5.9/gp/gpControl/setting/22/0')
        print('Set White Balance to Auto')
        sleep(1)

    if settings["settings"]["37"] != 0:
        requests.get('http://10.5.5.9/gp/gpControl/setting/24/0')
        print('Set ISO to 800')
        sleep(1)

else:
    if settings["settings"]["69"] != 2:
        requests.get('http://10.5.5.9/gp/gpControl/command/sub_mode?mode=1&sub_mode=2') # Night Mode
        print('Camera set to Single Night Mode')
        sleep(1)

    if settings["settings"]["22"] != 2:
        requests.get('http://10.5.5.9/gp/gpControl/setting/22/2')
        print('Set White Balance to Auto')
        sleep(1)

    if settings["settings"]["24"] != 1:
        requests.get('http://10.5.5.9/gp/gpControl/setting/24/1')
        print('Set ISO to 800')
        sleep(1)

# Set Standard Camera Settings
if settings["settings"]["20"] != 0:
    requests.get('http://10.5.5.9/gp/gpControl/setting/20/1')
    print("Spot Meter Turned Off")
    sleep(1)

if settings["settings"]["21"] != 1:
    requests.get('http://10.5.5.9/gp/gpControl/setting/21/1')
    print("ProTune Turned On")
    sleep(1)

if settings["settings"]["23"] != 0:
    requests.get('http://10.5.5.9/gp/gpControl/setting/23/0')
    print("Color Set to GoPro")
    sleep(1)

if settings["settings"]["25"] != 2:
    requests.get('http://10.5.5.9/gp/gpControl/setting/25/2')
    print('Set Sharpness to LOW')
    sleep(1)

# Take A Picture
r = requests.get('http://10.5.5.9/gp/gpControl/command/shutter?p=1')
if r.status_code == 200:
    print("New Picture Taken")
    sleep(10)
else:
    print("No Picture Taken")
    sleep(3)

# Get List of Pictures
r = requests.get('http://10.5.5.9//gp/gpMediaList')
jsonData = r.json()

images = jsonData["media"][0]["fs"]
oldestImage = min(images, key=lambda x:x['mod'])
newestImage = max(images, key=lambda x:x['mod'])
oldestImageFile = oldestImage['n']
newestImageFile = newestImage['n']

newestImageULR = "http://10.5.5.9:8080/videos/DCIM/100GOPRO/" + newestImageFile

# Download Newest Image
sleep(5)
downloadImg(newestImageULR)
print(newestImageFile + " downloaded as " + str(currentTime) + ".JPG")

# Delete Image
deleteImg(oldestImageFile)
print(oldestImageFile + " has been deleted.")

snapshot = re.search(r"[*0$]", str(currentTime))
if snapshot:
    print('create snapshot picture.')


