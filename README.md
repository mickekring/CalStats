# CalStats
 Retrieves data from your Google or (possibly) Apple calendar (haven't tested yet) and creates some statistics that might be useful to you (or your boss ;) )
 My stats are running live at https://mickekring.se/stats/time/ (in Swedish)
 
![v0_5](https://user-images.githubusercontent.com/10948066/124654275-ab980d80-de9e-11eb-9deb-3f576c32234b.jpg)

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

## Want to run it yourself?
* In not really ready to document this yet. It's still pretty much in development. 

## Version History
* 0.5 Added dates for x-axis on the charts for the 7 weeks. Minor clean up of code.
* 0.4 Added graph for hours worked, last 7 weeks.
* 0.2 Initial upload. Percentages per category since a date you choose. Percentages per category, last 7 weeks.

## Credits
The calendar import function in the script is based on jeinarsson work https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7
