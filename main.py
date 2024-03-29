from icalevents.icalevents import events
from datetime import datetime, timedelta
import pytz, paramiko, locale, yaml, os
import time
from dateutil import tz
import urllib.request
from tinydb import TinyDB, Query
import pandas as pd
import json


### Database and tables setup
db = TinyDB('calstats.json')
table_log_events = db.table('Events')
table_log_time = db.table('TimeHours')
table_stats = db.table('Stats')


# Things stored in database are:
# 	EventID, Category, Startdate, Enddate, Event, EventTimeSum

# Categories the script looks for in the calendar are:
# 	WEBB: SUPPORT: ADM: BESÖK: MÖTE: ITPED: KONF: UTV: MEDIA: LUNCH: DIV:


### Reads passwords, paths, sites to monitor and stuff from file
conf = yaml.load(open('config.yml'), Loader=yaml.FullLoader)


### SFTP file paths
localUrlPath = conf['paths']['localurlpath'] # Local path of php-files on the machine running the script - in credentials.xml
remoteUrlPath = conf['paths']['remoteurlpath'] # Remote path on SFTP server for php-files - in credentials.xml


### Set locale
locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')


# Start date from where calendar check starts | Year, Month, Day
#datetime_start = datetime(2021, 8, 10)
start_date = datetime(2022, 8, 7).astimezone(pytz.timezone('UTC'))
now_date = datetime.now().astimezone(pytz.timezone('UTC'))
my_timezone = pytz.timezone(conf['local']['timezone'])



### Log calendar events to database

def log_to_database(event_id, category, start, end, activity_day, event_time):

	table_log_events.insert({'EventID': event_id, 'Category': category, 'Startdate': str(start), 'Enddate': str(end)
		, 'Event': activity_day, 'EventTimeSum': str(event_time)})



### Log time events to database

def log_to_database_time(event_id, category, start, end, activity_day, event_time):

	table_log_time.insert({'EventID': event_id, 'Category': category, 'Startdate': str(start), 'Enddate': str(end)
		, 'Event': activity_day, 'EventTimeSum': str(event_time)})



### Main function for checking your work calendar for events

def read_main_work_calendar():

	url = conf['urlcalendar']['link_url_work_calendar']
	es = events(url, start=start_date, end=now_date)

	# Return start date from event
	
	def get_start(event):
		return event.start.astimezone(my_timezone)

	# Sort events earliest to latest
	
	es.sort(key=get_start)

	count = 1

	global cal_id_list

	cal_id_list = []

	for e in es:

		activity_day = e.summary
		# location = e.location - Could be used to show stats of where you spend your time 

		start = e.start.astimezone(my_timezone)
		end = e.end.astimezone(my_timezone)

		ev_id = e.uid
		cal_id_list.append(ev_id)

		event_time = end - start

		if "WEBB:" in activity_day:
			category = "Webb"
		elif "SUPPORT:" in activity_day:
			category = "Support"
		elif "ADM:" in activity_day:
			category = "Administration"
		elif "BESÖK:" in activity_day:
			category = "Besök"
		elif "MÖTE:" in activity_day:
			category = "Möte"
		elif "ITPED:" in activity_day:
			category = "IT-pedagog"
		elif "KONF:" in activity_day:
			category = "Konferens"
		elif "UTV:" in activity_day:
			category = "Egen utveckling"
		elif "MEDIA:" in activity_day:
			category = "Mediaproduktion"
		elif "LUNCH" in activity_day:
			category = "Lunch"
		elif "DIV:" in activity_day:
			category = "Diverse"
		else:
			category = "Okänt"

		global sum_all

		# Excluding category "Okänt" ( = Unknown) and "Lunch" from total sum
		
		if category == "Okänt" or category == "Lunch":
			pass

		else:
			if count == 1:
				sum_all = event_time
				count = 2

			else:
				sum_all = sum_all + event_time

		print("---------------")
		print("ID: " + ev_id)
		print("Category: " + category)
		print("Start time: " + str(start))
		print("End time: " + str(end))
		print("Event: " + activity_day)
		print("Time spent: " + str(event_time))
		print("---------------\n")
		print("Total time: " + str(sum_all))

		search_db = Query()

		# Checking if calendar event has been rescheduled or changed - and if, deletes it and relogs it in DB

		if table_log_events.search(search_db.EventID == ev_id):
			print("IN DB")

			if table_log_events.search(search_db.Startdate == str(start)) and table_log_events.search(search_db.Enddate == str(end)) and table_log_events.search(search_db.Event == activity_day):
				print("OK.")

			else: 
				print("Meeting has been changed.")
				table_log_events.remove(search_db.EventID == ev_id)
				print("Removed meeting from DB")
				log_to_database(ev_id, category, start, end, activity_day, event_time)
				print("Relogged meeting\n")

		else:
			print("NOT IN DB")
			log_to_database(ev_id, category, start, end, activity_day, event_time)



def read_time_calendar():

	
	url = conf['urlcalendar']['link_count_time_calendar']
	es = events(url, start=start_date, end=now_date)

	# Return start date from event
	
	def get_start(event):
		return event.start.astimezone(my_timezone)

	# Sort events earliest to latest
	
	es.sort(key=get_start)

	count = 1

	global cal_id_list_2

	cal_id_list_2 = []


	for e in es:

		activity_day = e.summary

		start = e.start.astimezone(my_timezone)
		end = e.end.astimezone(my_timezone)

		ev_id = e.uid
		cal_id_list_2.append(ev_id)

		event_time = end - start


		if "Aktivitet" in activity_day:
			category = "Activity"
		else:
			category = "Okänt"

		global sum_all_2

		# Excluding category "Okänt" ( = Unknown) and "Lunch" from total sum
		
		if category == "Okänt":
			pass

		else:
			if count == 1:
				sum_all_2 = event_time
				count = 2

			else:
				sum_all_2 = sum_all_2 + event_time

		print("---------------")
		print("ID: " + ev_id)
		print("Category: " + category)
		print("Start time: " + str(start))
		print("End time: " + str(end))
		print("Event: " + activity_day)
		print("Time spent: " + str(event_time))
		print("---------------\n")
		print("Total time: " + str(sum_all_2))

		search_db = Query()

		# Checking if calendar event has been rescheduled or changed - and if, deletes it and relogs it in DB

		if table_log_time.search(search_db.EventID == ev_id):
			print("IN DB")

			if table_log_time.search(search_db.Startdate == str(start)) and table_log_time.search(search_db.Enddate == str(end)) and table_log_time.search(search_db.Event == activity_day):
				print("OK.")

			else: 
				print("Meeting has been changed.")
				table_log_time.remove(search_db.EventID == ev_id)
				print("Removed meeting from DB")
				log_to_database_time(ev_id, category, start, end, activity_day, event_time)
				print("Relogged meeting\n")

		else:
			print("NOT IN DB")
			log_to_database_time(ev_id, category, start, end, activity_day, event_time)		



# Compares events in DB to calendar, to remove events that have been deleted in your calendar

def check_removed_events_in_database():

	search_db = Query()	

	db_id_list = [r['EventID'] for r in table_log_events]

	for e in cal_id_list:
		if e in db_id_list:
			db_id_list.remove(e)

	print("----EVENTS DELETED FROM CALENDAR----")
	print(db_id_list)
	print("------------------------------------")

	db_delete = db_id_list

	for d in db_delete:
		table_log_events.remove(search_db.EventID == d)

	# Looking into second table regarding time
	
	search_db = Query()	

	db_id_list_2 = [r['EventID'] for r in table_log_time]

	for e in cal_id_list_2:
		if e in db_id_list_2:
			db_id_list_2.remove(e)

	print("----EVENTS DELETED FROM CALENDAR----")
	print(db_id_list_2)
	print("------------------------------------")

	db_delete = db_id_list_2

	for d in db_delete:
		table_log_time.remove(search_db.EventID == d)	



# Sum of categories in percent and hours from datetime_start set

def sum_time_worked_by_categories_and_total():

	categories = ['Webb', 'Support', 'Administration', 'Besök', 'Möte', 'IT-pedagog', 'Konferens', 'Egen utveckling', 'Mediaproduktion', 'Diverse']
	listCat = []

	print("\n-----------------------\n")
	print("TIME SPENT - CATEGORIES")
	print("From: " + str(start_date) + "\n")
	
	days = sum_all.days
	days_to_hours = days * 24
	sec = sum_all.seconds
	hours = sec//3600
	hours_tot = hours + days_to_hours
	minutes = (sec//60)%60

	time = (str(hours_tot) + ":" + str(minutes) + ":00")

	print("Total time: " + str(time) + "\n")

	for cats in categories:

		search_db = Query()
		check_if_in_database = table_log_events.search(search_db.Category == cats)

		sum_list = []
		sort_round = 0

		for x in check_if_in_database:
			sum_list.append(x["EventTimeSum"])
		
		totalSecs = 0
		
		for tm in sum_list:
			timeParts = [int(s) for s in tm.split(':')]
			totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
		totalSecs, sec = divmod(totalSecs, 60)
		hr, min = divmod(totalSecs, 60)
		
		webb_time = (("%d:%02d:%02d") % (hr, min, sec))
		print(cats + "\nTime: " + webb_time)
		
		hh, mm, ss = map(int, time.split(':'))
		t1 = timedelta(hours=hh, minutes=mm, seconds=ss)
		hh, mm, ss = map(int, webb_time.split(':'))
		t2 = timedelta(hours=hh, minutes=mm, seconds=ss)
		percentage = (t2/t1)

		print("Percent: " + str(round(percentage * 100, 1)) + "%\n")
		perc_round = (str(round(percentage * 100)))

		if int(perc_round) < 10:
			sort_round = ("0" + str(perc_round))
		else:
			sort_round = perc_round

		if int(perc_round) > 29:
			color = "bg-danger"
		elif int(perc_round) > 19:
			color = "bg-warning"
		else:
			color = "bg-info"

		webb_time_strip = (("%d tim %02d min") % (hr, min))

		listCat.append('<p class="cattitle ' + str(sort_round) + '">' + cats + " | " + webb_time_strip + '</p><div class="progress"><div class="progress-bar ' + color + '" role="progressbar" style="width: ' + perc_round + '%" aria-valuenow="' + perc_round + '" aria-valuemin="0" aria-valuemax="100">' + perc_round + "%" + '</div></div>')
		listCat.sort(reverse=True)

	statusList = ("".join(listCat))

	with open("web/status.php", "w") as f2:
			f2.write(statusList)



# Sum the time that should have been worked and total

def sum_time_i_should_have_worked():

	categories = ['Activity']
	listCat = []

	print("\n-----------------------\n")
	print("TIME THAT SHOULD HAVE BEEN WORKED")
	print("From: " + str(start_date) + "\n")
	
	days = sum_all_2.days
	days_to_hours = days * 24
	sec = sum_all_2.seconds
	hours = sec//3600
	hours_tot = hours + days_to_hours
	minutes = (sec//60)%60

	time_2 = (str(hours_tot) + ":" + str(minutes) + ":00")

	print("Total time to work: " + str(time_2) + "\n")

	for cats in categories:

		search_db = Query()
		check_if_in_database = table_log_time.search(search_db.Category == cats)

		sum_list = []
		sort_round = 0

		for x in check_if_in_database:
			sum_list.append(x["EventTimeSum"])
		
		totalSecs = 0
		
		for tm in sum_list:
			timeParts = [int(s) for s in tm.split(':')]
			totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
		totalSecs, sec = divmod(totalSecs, 60)
		hr, min = divmod(totalSecs, 60)
		
		webb_time = (("%d:%02d:%02d") % (hr, min, sec))
		print(cats + "\nTime: " + webb_time)
		
		hh, mm, ss = map(int, time_2.split(':'))
		t1 = timedelta(hours=hh, minutes=mm, seconds=ss)
		hh, mm, ss = map(int, webb_time.split(':'))
		t2 = timedelta(hours=hh, minutes=mm, seconds=ss)
		percentage = (t2/t1)

		print("Percent: " + str(round(percentage * 100, 1)) + "%\n")
		perc_round = (str(round(percentage * 100)))

		if int(perc_round) < 10:
			sort_round = ("0" + str(perc_round))
		else:
			sort_round = perc_round

		if int(perc_round) > 29:
			color = "bg-danger"
		elif int(perc_round) > 19:
			color = "bg-warning"
		else:
			color = "bg-info"

		webb_time_strip = (("%d tim %02d min") % (hr, min))

	#with open("web/status.php", "w") as f2:
	#		f2.write(statusList)



# Uploads php files to your sftp / web server

def upload_files_to_webserver():
	
	try:
		host = conf['sftp']['host']
		port = conf['sftp']['port']
		transport = paramiko.Transport((host, port))

		password = conf['sftp']['password']
		username = conf['sftp']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir(remoteUrlPath)

		filepath1 = "time.php"
		localpath1 = localUrlPath + "web/time.php"

		filepath2 = "status.php"
		localpath2 = localUrlPath + "web/status.php"

		filepath3 = "7weekcats.php"
		localpath3 = localUrlPath + "web/7weekcats.php"

		filepath4 = "7weekhours.php"
		localpath4 = localUrlPath + "web/7weekhours.php"

		filepath5 = "calstats.json"
		localpath5 = localUrlPath + "calstats.json"

		filepath6 = "plusminus.php"
		localpath6 = localUrlPath + "web/plusminus.php"

		filepath7 = "worktime.php"
		localpath7 = localUrlPath + "web/worktime.php"

		filepath8 = "actualworktime.php"
		localpath8 = localUrlPath + "web/actualworktime.php"

		filepath9 = "calstats.xlsx"
		localpath9 = localUrlPath + "web/calstats.xlsx"

		sftp.put(localpath1, filepath1)
		sftp.put(localpath2, filepath2)
		sftp.put(localpath3, filepath3)
		sftp.put(localpath4, filepath4)
		sftp.put(localpath5, filepath5)
		sftp.put(localpath6, filepath6)
		sftp.put(localpath7, filepath7)
		sftp.put(localpath8, filepath8)
		sftp.put(localpath9, filepath9)

		sftp.close()
		transport.close()

		print("\n>>> Files Successfully uploaded.")
	
	except:
		
		print("\n>>> Error. Files unable to upload.\nWeb server might be down.")	
		pass



# Sums all time you have scheduled divided by the amount of hours you should have worked.

def modules_plus_minus_time():

	days = sum_all.days
	days_to_hours = days * 24
	sec = sum_all.seconds
	hours = sec//3600
	hours_tot = hours + days_to_hours
	minutes = (sec//60)%60
	

	if minutes < 10:
		minutes = "00"
	else:
		pass
	
	time_calculate = (str(hours_tot) + ":" + str(minutes) + ":00")
	time = (str(hours_tot) + ' <span class="tim">TIM</span> ' + str(minutes) + ' <span class="tim">MIN</span>')

	minutes_from_hours = int(hours_tot) * 60
	minutes_total = minutes_from_hours + int(minutes)

	print(minutes_total)
	print("Total time worked: " + str(time) + "\n")

	days = sum_all_2.days
	days_to_hours = days * 24
	sec = sum_all_2.seconds
	hours = sec//3600
	hours_tot = hours + days_to_hours
	minutes = (sec//60)%60

	if minutes < 10:
		minutes = "00"
	else:
		pass
	
	time_calculate_2 = (str(hours_tot) + ":" + str(minutes) + ":00")
	time_2 = (str(hours_tot) + ' <span class="tim">TIM</span> ' + str(minutes) + ' <span class="tim">MIN</span>')

	minutes_from_hours = int(hours_tot) * 60
	minutes_total_2 = minutes_from_hours + int(minutes)
	print(minutes_total_2)

	print("Total time worked: " + str(time) + "\n")


	# Calculate time difference

	difference_work = (minutes_total - minutes_total_2) / 60
	print(difference_work)

	if difference_work < 0:

		sumDiv = round(difference_work, 1)

		if sumDiv < 5:
			p_color = "#7db53f"
		else:
			p_color = "#0dcaf0"

		print("\nDu har jobbat för lite. Du skulle ha jobbat " + str(sumDiv) + " timmar mer.")
		
		plusminus_html = '<div class="divbox"><p class="boxtitle"><strong>Tid</strong>Balans</p><p class="boxnumber" style="color: ' + p_color + '"">' + str(sumDiv) + ' <span class="tim">TIM</span></p><p>Jobba mer! Sluta slacka och lägg på ett kol.</p></div>'

	else:
		sumDiv = round(difference_work, 1)

		if sumDiv < 5:
			p_color = "#7db53f"
		else:
			p_color = "#be2d2c"

		print("\nDu har jobbat för mycket. Du skulle ha jobbat " + str(sumDiv) + " timmar mindre.")

		plusminus_html = '<div class="divbox"><p class="boxtitle"><strong>Tid</strong>Balans</p><p class="boxnumber" style="color: ' + p_color + '"">+' + str(sumDiv) + ' <span class="tim">TIM</span></p><p>Jobba mindre! Gå hem lite tidigare eller ta en dag ledigt.</p></div>'


	workhours_html = '<div class="divbox"><p class="boxtitle"><strong>Arbets</strong>tid</p><p class="boxnumber">' + str(time_2) + '</p><p>Förväntad arbetad tid sedan 09 aug 2021.</p></div>'

	actual_workhours_html = '<div class="divbox"><p class="boxtitle"><strong>Arbetad</strong> tid</p><p class="boxnumber">' + str(time) + '</p><p>Faktiskt arbetad tid sedan 09 aug 2021.</p></div>'


	with open("web/worktime.php", "w") as f2:
			f2.write(workhours_html)

	with open("web/actualworktime.php", "w") as f2:
			f2.write(actual_workhours_html)
	
	with open("web/plusminus.php", "w") as f2:
			f2.write(plusminus_html)



# Sums stats of categories in percent for last 7 weeks including working hours

def Stats7weeks():

	search_db = Query()
	utc=pytz.UTC

	weeks = 8 # One extra for the loop
	week = 1

	cat_list = ['Administration', 'Webb', 'Mediaproduktion', 'IT-pedagog', 'Möte', 'Egen utveckling', 'Support'] 

	total_timeList = []
	total_timeList_month = []
	timeList_weeks_in_month = []
	catTime = []
	catTime_ADM = []
	catTime_WEBB = []
	catTime_MEDIA = []
	catTime_ITPED = []
	catTime_MOTE = []
	catTime_UTV = []
	catTime_SUP = []

	date_x_list = []
	
	# Stores the whole DB to a list
	db_get_start = table_log_events.all()


	######## TOTAL - 49 days split into 7 weeks. Total time and weekly time #########

	month_days = 7
	month_offset = 0

	while week != weeks:

		total_timeList_week = []

		if week == 7:
			month_days = 7
			month_offset = 0
		elif week == 6:
			month_days = 14
			month_offset = 7
		elif week == 5:
			month_days = 21
			month_offset = 14
		elif week == 4:
			month_days = 28
			month_offset = 21
		elif week == 3:
			month_days = 35
			month_offset = 28
		elif week == 2:
			month_days = 42
			month_offset = 35
		elif week == 1:
			month_days = 49
			month_offset = 42

		while month_days != month_offset:

			startQueryDate = datetime.now(utc) - timedelta(days=month_days)
			startQueryDate_strip = startQueryDate.strftime("%Y-%m-%d")

			db_get_start_len = len(db_get_start)

			for x in range(db_get_start_len):

				if startQueryDate_strip in (db_get_start[x]['Startdate']) and "Okänt" not in (db_get_start[x]['Category']):
					time = (db_get_start[x]['EventTimeSum'])
					total_timeList_week.append(time)

				else:
					pass

			# Gets last date of each week for x-axis on the charts

			if month_days == 1 or month_days == 8 or month_days == 15 or month_days == 22 or month_days == 29 or month_days == 36 or month_days == 43:
				date_x_list.append(startQueryDate_strip)
			else: 
				pass

			month_days -= 1

		totalSecs = 0
		for tm in total_timeList_week:
			timeParts = [int(s) for s in tm.split(':')]
			totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
		totalSecs, sec = divmod(totalSecs, 60)
		hr, min = divmod(totalSecs, 60)
		timeList_weeks_in_month.append("%d:%02d:%02d" % (hr, min, sec))

		week += 1


	for tm in timeList_weeks_in_month:
		timeParts = [int(s) for s in tm.split(':')]
		totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
	totalSecs, sec = divmod(totalSecs, 60)
	hr, min = divmod(totalSecs, 60)
	total_timeList_month.append("%d:%02d:%02d" % (hr, min, sec))


	######## CATEGORIES week by week ##########

	weeks = 8 # One extra for the loop
	week = 1

	
	while week != weeks:

		for cat in cat_list:

			if week == 7:
				week_days = 7
				day_offset = 0
			elif week == 6:
				week_days = 14
				day_offset = 7
			elif week == 5:
				week_days = 21
				day_offset = 14
			elif week == 4:
				week_days = 28
				day_offset = 21
			elif week == 3:
				week_days = 35
				day_offset = 28
			elif week == 2:
				week_days = 42
				day_offset = 35
			elif week == 1:
				week_days = 49
				day_offset = 42

			timeList = []
			
			# Week and category

			print("Looping through categories: " + cat)
		
			while week_days != day_offset:

				startQueryDate = datetime.now(utc) - timedelta(days=week_days)
				startQueryDate_strip = startQueryDate.strftime("%Y-%m-%d")

				#print(startQueryDate_strip)

				db_get_start_len = len(db_get_start)

				for x in range(db_get_start_len):

					if startQueryDate_strip in (db_get_start[x]['Startdate']) and cat in (db_get_start[x]['Category']):

						time = (db_get_start[x]['EventTimeSum'])
						timeList.append(time)
						total_timeList.append(time)

					else:
						pass

				week_days -= 1


			totalSecs = 0
			for tm in timeList:
				timeParts = [int(s) for s in tm.split(':')]
				totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
			totalSecs, sec = divmod(totalSecs, 60)
			hr, min = divmod(totalSecs, 60)
			print("Total time: " + cat + " | Week " + str(week))
			print("%d:%02d:%02d" % (hr, min, sec))
			print("")
			
			if cat == "Administration":
				catTime_ADM.append("%d:%02d:%02d" % (hr, min, sec))
			elif cat == "Webb":
				catTime_WEBB.append("%d:%02d:%02d" % (hr, min, sec))
			elif cat == "Mediaproduktion":
				catTime_MEDIA.append("%d:%02d:%02d" % (hr, min, sec))
			elif cat == "IT-pedagog":
				catTime_ITPED.append("%d:%02d:%02d" % (hr, min, sec))
			elif cat == "Möte":
				catTime_MOTE.append("%d:%02d:%02d" % (hr, min, sec))
			elif cat == "Egen utveckling":
				catTime_UTV.append("%d:%02d:%02d" % (hr, min, sec))
			elif cat == "Support":
				catTime_SUP.append("%d:%02d:%02d" % (hr, min, sec))

		week += 1

	print("ADM Category total w 1-7: " + str(catTime_ADM))
	print("WEBB Category total w 1-7: " + str(catTime_WEBB))
	print("MEDIA Category total w 1-7: " + str(catTime_MEDIA))
	print("ITPED Category total w 1-7: " + str(catTime_ITPED))
	print("MÖTE Category total w 1-7: " + str(catTime_MOTE))
	print("UTV Category total w 1-7: " + str(catTime_UTV))
	print("SUP Category total w 1-7: " + str(catTime_SUP))
	print("SUM all - total w 1-7: " + str(timeList_weeks_in_month))

	date_x_list = str(date_x_list)
	date_x_list = date_x_list.replace("'",'"')
	date_x_list = date_x_list.replace("[","")
	date_x_list = date_x_list.replace("]","")

	print("Dates for x axis: " + date_x_list)


	for cat in cat_list: 

		percList = []

		if cat == "Administration":
			catTime = catTime_ADM
		elif cat == "Webb":
			catTime = catTime_WEBB
		elif cat == "Mediaproduktion":
			catTime = catTime_MEDIA
		elif cat == "IT-pedagog":
			catTime = catTime_ITPED
		elif cat == "Möte":
			catTime = catTime_MOTE
		elif cat == "Egen utveckling":
			catTime = catTime_UTV
		elif cat == "Support":
			catTime = catTime_SUP

		for x in range(7):
			l1 = str([catTime [x]])	
			l2 = str([timeList_weeks_in_month [x]])

			totalSecs = 0

			for tm in ([catTime [x]]):
				timeParts = [int(s) for s in tm.split(':')]
				totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
			totalSecs, sec = divmod(totalSecs, 60)
			hr, min = divmod(totalSecs, 60)

			cat_time = (("%d:%02d:%02d") % (hr, min, sec))

			totalSecs = 0

			for tm in ([timeList_weeks_in_month [x]]):
				timeParts = [int(s) for s in tm.split(':')]
				totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
			totalSecs, sec = divmod(totalSecs, 60)
			hr, min = divmod(totalSecs, 60)

			tot_time = (("%d:%02d:%02d") % (hr, min, sec))

			hh, mm, ss = map(int, cat_time.split(':'))
			t1 = timedelta(hours=hh, minutes=mm, seconds=ss)
			hh, mm, ss = map(int, tot_time.split(':'))
			t2 = timedelta(hours=hh, minutes=mm, seconds=ss)

			# If no total time exists, eg if you are on vacation, it skips division which causes error because of zero division,
			# and sets the percentage to zero.			
			if t2 == timedelta(0, 00, 00):
				perc_round = 0
				percList.append(perc_round)

			else:
				percentage = (t1/t2)
				perc_round = (str(round(percentage * 100)))
				percList.append(perc_round)
		
		percList = str(percList)
		percList = percList.replace("'","")
		percList = percList.replace("[","")
		percList = percList.replace("]","")

		print("Procent: " + percList)

		if cat == "Administration":
			percList_ADM = percList
		elif cat == "Webb":
			percList_WEBB = percList
		elif cat == "Mediaproduktion":
			percList_MEDIA = percList
		elif cat == "IT-pedagog":
			percList_ITPED = percList
		elif cat == "Möte":
			percList_MOTE = percList
		elif cat == "Egen utveckling":
			percList_UTV = percList
		elif cat == "Support":
			percList_SUP = percList


	html_cat = ('<script> const labels = [' + date_x_list + ']; const NUMBER_CFG = {min: 0, max: 100}; const data = {labels: labels, datasets: [{ label: "Administration", data: [' 
		+ percList_ADM + '], borderColor: "rgb(255, 99, 132)", backgroundColor: "rgb(255, 99, 132)",}, { label: "IT-pedagog", data: [' 
		+ percList_ITPED + '], borderColor: "#7db53f", backgroundColor: "#7db53f",}, { label: "Egen utveckling", data: [' 
		+ percList_UTV + '], borderColor: "#bf2c2c", backgroundColor: "#bf2c2c",}, { label: "Support", data: [' 
		+ percList_SUP + '], borderColor: "#3580dc", backgroundColor: "#3580dc",}, { label: "Möten", data: [' 
		+ percList_MOTE + '], borderColor: "#6d35dc", backgroundColor: "#6d35dc",}, {label: "Webb", data: [' 
		+ percList_WEBB +'], borderColor: "#0dcaf0", backgroundColor: "#0dcaf0",}, {label: "Mediaproduktion", data: [' 
		+ percList_MEDIA + '], borderColor: "#ffc107", backgroundColor: "#ffc107",}]}; const config = {type: "line", data: data, options: {color: "#ffffff", responsive: true, plugins: {legend: {position: "top",}, } }, }; var myChart = new Chart(document.getElementById("myChart30"), config);</script>')

	with open("web/7weekcats.php", "w") as f2:
			f2.write(html_cat)

	timeList_weeks_in_month = str(timeList_weeks_in_month)
	timeList_weeks_in_month = timeList_weeks_in_month.replace(":00","")
	timeList_weeks_in_month = timeList_weeks_in_month.replace(":",".")
	timeList_weeks_in_month = timeList_weeks_in_month.replace("'","")
	timeList_weeks_in_month = timeList_weeks_in_month.replace("[","")
	timeList_weeks_in_month = timeList_weeks_in_month.replace("]","")

	html_hours = ('<script> const labels2 = [' + date_x_list + ']; const NUMBER_CFG2 = {min: 0, max: 100}; const data2 = {labels: labels2, datasets: [{ label: "' 
		+ '40' + ' TIMMAR", data: [' + '40' + ', ' + '40' 
		+ ', ' + '40' + ', ' + '40' + ', ' + '40' + ', ' 
		+ '40' + ', ' + '40' + '], borderColor: "rgb(255, 99, 132)", backgroundColor: "rgb(255, 99, 132)", borderDash: [5, 5],}, {label: "ARBETAD TID", data: [' 
		+ timeList_weeks_in_month + '], borderColor: "#ffc107", backgroundColor: "#ffc107",}]}; const config2 = {type: "line", data: data2, options: {color: "#ffffff", responsive: true, plugins: {legend: {position: "top",}, } }, }; var myChart2 = new Chart(document.getElementById("myChart1"), config2);</script>')

	with open("web/7weekhours.php", "w") as f3:
			f3.write(html_hours)



def FileSize():

	global file_size_bytes_json
	global file_size_bytes_xlsx

	file_size_json = os.stat('calstats.json')
	file_size_bytes_json = (str(file_size_json.st_size) + " bytes")

	file_size_xlsx = os.stat('web/calstats.xlsx')
	file_size_bytes_xlsx = (str(file_size_xlsx.st_size) + " bytes")



# Converts JSON file to Excel

def JSONtoExcel():

	json_data = json.loads(open('calstats.json').read())

	rows = []

	for x in (json_data['Events']):
		event = (json_data['Events'][x]['Event'])
		category = (json_data['Events'][x]['Category'])
		startdate = (json_data['Events'][x]['Startdate'])
		enddate = (json_data['Events'][x]['Enddate'])
		total_time = (json_data['Events'][x]['EventTimeSum'])

		rows.append([startdate, enddate, total_time ,category, event])

	df = pd.DataFrame(rows, columns = ['Start date','End date','Total time', 'Category', 'Event'])
	writer = pd.ExcelWriter('web/calstats.xlsx', engine = 'xlsxwriter')
	df.to_excel(writer, sheet_name = 'calstats', index = False)
	writer.save()



# Gets time and creates a updated time php page

def TimeNow():
	global klNu
	global day
	global date
	global month


	now = datetime.now()
	year = now.strftime("%Y")
	month = now.strftime("%B")
	date = now.strftime("%d")
	day = now.strftime("%A")

	klNu = now.strftime("%H:%M")


	print(klNu)
	print(day)

	styleTime = ''

	with open("web/time.php", "w") as f1:
		f1.write(styleTime + '<h1 class="clock"><i class="far fa-clock" aria-hidden="true"></i> ' 
			+ klNu + '</h1><h4><strong>SENAST</strong> UPPDATERAT<br />' + day + ' | ' + date + ' ' 
			+ month + ' ' + year + ' | ' + klNu + '</h4><p class"download"><i class="fas fa-file-download"></i> <a href="calstats.json">Ladda ned JSON (' 
			+ file_size_bytes_json + ')</a></p><p class"download"><i class="fas fa-file-excel"></i> <a href="calstats.xlsx">Ladda ned XLSX (' 
			+ file_size_bytes_xlsx + ')</a></p>')



# Main loop

def Main():

	while True:

		try:

			read_main_work_calendar() # New check works
			read_time_calendar() # New check works
			check_removed_events_in_database() 
			sum_time_worked_by_categories_and_total() 
			sum_time_i_should_have_worked() 
			Stats7weeks() 
			modules_plus_minus_time() 
			JSONtoExcel() 
			FileSize() 
			TimeNow()
			upload_files_to_webserver() 
			time.sleep(600) 

		except:
			print("Error. Going to sleep...")
			time.sleep(600)

# ------------------------------


### MAIN PROGRAM ###

if __name__ == "__main__":
	Main()
