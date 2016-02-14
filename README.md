#GoPro Timelapse
This is a python script that will take a series of pictures using a GoPro Hero4. The basis for the commands are from [here](https://github.com/ztzhang/GoProWifiCommand). 

![image](https://www.cinema5d.com/wp-content/uploads/2015/02/gopro-hero4-new-camera-black-silver-editions-600x342.png)


##Usage
The current implementation of this script is to be run via CRON. The interval you set to run this via CRON is how often a picture will be taken. To run this every minute, enter this command in CRON.


	* * * * * python3 main.py >/dev/null 2>&1

If you want to run this at a different interval, you can create your CRON command [here](http://crontab-generator.org/).

##Current Features
* Save picture on every run of script
* Pictures saved to individual folders for each day 
* Pictures will be named HHMM.JPG (24 hour time) so they can be imported chronologically
* Deletes images off GoPro memory card to save space
* Can save a picture every 10 minutes as a "snapshot" to be uploaded to a website
