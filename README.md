# CalStats
 Retrieves data from your Google or Apple calendar and creates some statistics that might be useful to you (or your boss ;) )
 My stats are running live at https://mickekring.se/stats/time/
 
![v0_3](https://user-images.githubusercontent.com/10948066/124362857-f237fe80-dc37-11eb-8585-c4f550530f4b.jpg)

## What is it and what does it do?
It's a Python script that reads your calendar - and based on the prefix of the name of your calendar events, it creates statistics from it. Then it updates a website so that you can view it in a more user friendly way.

I plan everything in my calendar and name the calendar events with prefixes like; 'ADM: Schedule', 'WEB: Blogs' and so on. The script then groups all 'ADM:', 'WEB:' and other categories (hard coded in the script), calculates the time and divides it by the total time to get some percentages and other stuff.

![cal](https://user-images.githubusercontent.com/10948066/124256060-283b8c80-db2b-11eb-93fe-8a4928c986e2.jpg)

## Disclaimer
__I'm not a coder__. I just like to create stuff. :)

## Built with
* Python 3.x https://www.python.org/
* Bootstrap 5.x https://getbootstrap.com/
* Chart JS https://www.chartjs.org/
* Font Awesome https://fontawesome.com/

## Version History
* 0.3 Added graph for hours worked, latest 7 weeks.
* 0.2 Initial upload. 

## Credits
The calendar import function in the script is based on jeinarsson work https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7
