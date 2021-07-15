# CalStats
 Retrieves data from your Google or (possibly) Apple calendar (haven't tested yet) and creates some statistics that might be useful to you (or your boss ;) )
 My stats are running live at https://mickekring.se/stats/time/ (in Swedish)
 
![calstats0_6](https://user-images.githubusercontent.com/10948066/125815584-c60c044b-d7b0-43fc-aee9-c7edee45f8eb.jpg)
___Image above showing front end___

## What is this? And what does it do?
I plan everything work related in my calendar and name the calendar events with prefixes like; '__ADM:__ Schedule' (ADM = Administration), '__WEB:__ Blogs' and so on. The script then groups all 'ADM:', 'WEB:' and other categories (hard coded in the script), calculates the time and divides it by the total time to get some percentages and other stuff that is useful to me. Simply put, it's a tool for me to make sure I spend my time well.

The Python script runs on a Raspberry Pi and fetches and updates statistics every 10 minutes, uploads the php-files to my web server via sftp.

![cal](https://user-images.githubusercontent.com/10948066/124256060-283b8c80-db2b-11eb-93fe-8a4928c986e2.jpg)

## Disclaimer
__I'm not a coder__. I just like to create stuff. :)

## Built with
* Python 3.x https://www.python.org/
* Bootstrap 5.x https://getbootstrap.com/
* Chart JS https://www.chartjs.org/
* Font Awesome https://fontawesome.com/

# Want to run it yourself?

This script is sort of tailored to my needs, so if you'd like to run it, you'll have to change a couple of things. Mainly names of the categories you'd like to track and in that case, some conditions. Since I'm not a coder, I haven't (yet) been able to set all things you have to change as constant variables or lists, but I'll do my best to guide you.

__WHAT YOU NEED__
* A device that can run Python 3.x
* A web server with php support
* An sftp server (on your web server) that the script uses to upload files to your web server
* A public Google calendar (or Apple calendar)

__SETUP__
* Download all files to a folder of your choice
* Open credentials.yml and change sftp account information, paths - both local url (where you run the script) and remote (on your web server) and the url to your public calendar .ics file
* Open index.php and edit the title and headings that you want to display on your front end
* Upload index.php and style.css to your web server
* Open calstats.py and change the following:
  * Line 39 | Locale
  * Line 43 | Ajust for summer / winter time
  * Line 51 | Start date from when the script should start track
  * Line 109-132 | Enter your own category prefixes and category names that you want to track
  * Line 138 | Exclude calendar events like lunch and unknown
  * Line 213 | Modify the categories you want to track
  * Line 350-362 | Modify the categories you want 7 week stats of and change/create lists names
  * Line 410 | Exclude if you have a "unknown" (Okänt in swedish) category
  * Line 516 - 540 | Change to your categories
  * Line 554 - 567 | Change to your categories
  * Line 616 - 629 | Change to your categories
  * Line 632 - 640 | Change to your categories
  * Line 651 - 652 | Change the second graph html output
  * Line 692 - 695 | Modify time text
  * Line 714 | Modify how often you want the main loop to run in seconds


__INSTALL PYTHON MODULES__
* Pytz - pip3 install pytz
* Paramiko - pip3 install paramiko
* YAML - pip3 install pyyaml
* TinyDB - pip3 install tinydb
* Datetime - pip3 install datetime

__RUN__
* Run calstats.py

## Version History
* 0.6.1 Added download link for JSON database on front end generated by calstats.py
* 0.6 Added uploading of the json database file to the web server and fixed a bug that occurs when there is zero worked total time (e g when on vacation) which caused zero division. 
* 0.5 Added dates for x-axis on the charts for the 7 weeks. Minor clean up of code.
* 0.4 Added graph for hours worked, last 7 weeks.
* 0.2 Initial upload. Percentages per category since a date you choose. Percentages per category, last 7 weeks.

## Credits
The calendar import function in the script is based on jeinarsson work https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7
