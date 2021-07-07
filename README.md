# CalStats
 Retrieves data from your Google or (possibly) Apple calendar (haven't tested yet) and creates some statistics that might be useful to you (or your boss ;) )
 My stats are running live at https://mickekring.se/stats/time/ (in Swedish)
 
![v0_5](https://user-images.githubusercontent.com/10948066/124654275-ab980d80-de9e-11eb-9deb-3f576c32234b.jpg)

## What is it and what does it do?
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

## Want to run it yourself?

__!DOCUMENTATION IS NOT READY AT THIS POINT!__

__WHAT YOU NEED__
* A device that can run Python 3.x
* A web server with php support
* An sftp server that the script uses to upload files to your web server
* A public Google calendar (or Apple calendar)

__SETUP__
* Download all files to a folder of your choice
* Open credentials.yml and change sftp account information, paths - both local url (where you run the script) and remote (on your web server) and the url to your calendar .ics file
* Open index.php and change the title and headings
* Open calstats.py and..........

__INSTALL PYTHON MODULES__
* Pytz - pip3 install pytz
* Paramiko - pip3 install paramiko
* YAML - pip3 install pyyaml
* TinyDB - pip3 install tinydb
* Datetime - pip3 install datetime

__RUN__
* Run calstats.py

## Version History
* 0.5 Added dates for x-axis on the charts for the 7 weeks. Minor clean up of code.
* 0.4 Added graph for hours worked, last 7 weeks.
* 0.2 Initial upload. Percentages per category since a date you choose. Percentages per category, last 7 weeks.

## Credits
The calendar import function in the script is based on jeinarsson work https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7
