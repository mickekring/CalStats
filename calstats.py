

import math, pytz, paramiko, locale, yaml, os, sys, requests, signal
from time import strftime
import time as t
from dateutil import tz
import datetime
import urllib.request
from ics import *
from tinydb import TinyDB, Query


### Database and tables setup
db = TinyDB('calstats.json')

table_log_events = db.table('Events')
table_stats = db.table('Stats')


### Reads passwords, paths, sites to monitor and stuff from file
conf = yaml.load(open('credentials.yml'), Loader=yaml.FullLoader)


### SFTP file paths
localUrlPath = conf['paths']['localurlpath'] # Local path of php-files on the machine running the script - in credentials.xml
remoteUrlPath = conf['paths']['remoteurlpath'] # Remote path on SFTP server for php-files - in credentials.xml


### Set locale
locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')


## Load config and credentials
conf = yaml.load(open('credentials.yml'), Loader=yaml.FullLoader)


# Adjust in hours for summer / winter time
time_adjust = 2


# Adjust in hours for how long forwards the script should check your calendar
check_time = 168

# Start date from where calendar check starts | Year, Month, Day
datetime_start = datetime(2021, 5, 1)


# ------------------------------


### Log calendar events to database
def logging(event_id, category, start, end, activity_day, event_time):

	table_log_events.insert({'EventID': event_id, 'Category': category, 'Startdate': str(start), 'Enddate': str(end), 'Event': activity_day, 'EventTimeSum': str(event_time)})


### Main function for checking calendar for events
def Calendar():

	url = conf['urlcalendar']['link_url']

	with urllib.request.urlopen(url) as response:
		ics_string = response.read()

	utc=pytz.UTC
	window_start = datetime_start.replace(tzinfo=utc)
	
	window_end = datetime.now(utc)
	#window_end = datetime.now(utc) + timedelta(hours=(check_time))
	events = get_events_from_ics(ics_string, window_start, window_end)

	count = 1

	global cal_id_list
	cal_id_list = []

	for e in events:
		activity_day = ('{}'.format(e['summary']))
		start = (e['startdt'] + timedelta(hours=(time_adjust)))
		start_date_day = (start.strftime("%a"))
		start_time_day = (start.strftime("%H:%M"))
		start_time_h = (start.strftime("%H"))
		start_time_hour = (int(start_time_h))
		start_time_min = (start.strftime("%M"))

		ev_id = (e['uid'])
		cal_id_list.append(ev_id)

		end = (e['enddt'] + timedelta(hours=(time_adjust)))
		end_date = (end.strftime("%Y-%m-%d"))
		end_time_h = (end.strftime("%H"))
		end_time_hour = (int(end_time_h) + 1)
		end_time_min = (end.strftime("%M"))

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

		# Excluding category "Okänt" and "Lunch" from total sum
		
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
		print("Kategori: " + category)
		print("Starttid: " + str(start))
		print("Sluttud: " + str(end))
		print("Event: " + activity_day)
		print("Tidsåtgång: " + str(event_time))
		print("---------------\n")
		print("Total tid: " + str(sum_all))

		search_db = Query()

		# Checking if calendar event has been rescheduled or changed - and if, deletes it and relogs it

		if table_log_events.search(search_db.EventID == ev_id):
			print("IN DB")
			if table_log_events.search(search_db.Startdate == str(start)) and table_log_events.search(search_db.Enddate == str(end)) and table_log_events.search(search_db.Event == activity_day):
				print("OK.")
			else: 
				print("Meeting has been changed.")
				table_log_events.remove(search_db.EventID == ev_id)
				print("Removed meeting from DB")
				logging(ev_id, category, start, end, activity_day, event_time)
				print("Relogged meeting\n")

		else:
			print("NOT IN DB")
			logging(ev_id, category, start, end, activity_day, event_time)
		

def removedEvents():

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


def sumTimeCat():

	categories = ['Webb', 'Support', 'Administration', 'Besök', 'Möte', 'IT-pedagog', 'Konferens', 'Egen utveckling', 'Mediaproduktion', 'Diverse']
	listCat = []

	print("\n-----------------------\n")
	print("TIME SPENT - CATEGORIES")
	print("From: " + str(datetime_start) + "\n")
	
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

	with open("status.php", "w") as f2:
			f2.write(statusList)


def FileuUploads():
	
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
		localpath1 = localUrlPath + "time.php"

		filepath2 = "status.php"
		localpath2 = localUrlPath + "status.php"

		filepath3 = "7weekcats.php"
		localpath3 = localUrlPath + "7weekcats.php"

		filepath4 = "7weekhours.php"
		localpath4 = localUrlPath + "7weekhours.php"

		sftp.put(localpath1, filepath1)
		sftp.put(localpath2, filepath2)
		sftp.put(localpath3, filepath3)
		sftp.put(localpath4, filepath4)

		sftp.close()
		transport.close()

		print("\n>>> Files Successfully uploaded.")
	
	except:
		
		print("\n>>> Error. Files unable to upload.")	
		pass

def Stats7weeks():

	search_db = Query()
	utc=pytz.UTC

	weeks = 8 # One extra for the loop
	week = 1

	#cat_list = ['Webb', 'Support', 'Administration', 'Besök', 'Möte', 'IT-pedagog', 'Konferens', 'Egen utveckling', 'Mediaproduktion', 'Diverse']
	cat_list = ['Administration', 'Webb', 'Mediaproduktion', 'IT-pedagog', 'Möte', 'Egen utveckling', 'Support'] # Test

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
	
	# Stores the whole DB to a list
	db_get_start = table_log_events.all()


	######## TOTAL Month - 49 days split into 7 weeks. Total time and weekly time #########

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
			month_days -= 1

		totalSecs = 0
		for tm in total_timeList_week:
		    timeParts = [int(s) for s in tm.split(':')]
		    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
		totalSecs, sec = divmod(totalSecs, 60)
		hr, min = divmod(totalSecs, 60)
		timeList_weeks_in_month.append("%d:%02d:%02d" % (hr, min, sec))

		week += 1

	#print("Summa totalt veckor 1-5: " + str(timeList_weeks_in_month))

	for tm in timeList_weeks_in_month:
	    timeParts = [int(s) for s in tm.split(':')]
	    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
	totalSecs, sec = divmod(totalSecs, 60)
	hr, min = divmod(totalSecs, 60)
	total_timeList_month.append("%d:%02d:%02d" % (hr, min, sec))

	#print("Summa totalt alla veckor: " + str(total_timeList_month))

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
			
			# Vecka och kategori

			print("Kategori att loopa: " + cat)
		
			while week_days != day_offset:

				startQueryDate = datetime.now(utc) - timedelta(days=week_days)
				startQueryDate_strip = startQueryDate.strftime("%Y-%m-%d")

				#print(startQueryDate_strip)

				db_get_start_len = len(db_get_start)

				for x in range(db_get_start_len):

					if startQueryDate_strip in (db_get_start[x]['Startdate']) and cat in (db_get_start[x]['Category']):
						#print("------")
						#print(db_get_start[x]['Category'])
						#print(db_get_start[x]['Event'])
						time = (db_get_start[x]['EventTimeSum'])
						#print(time)
						#print("------")
						timeList.append(time)
						total_timeList.append(time)

					else:
						pass

				week_days -= 1

			#print(timeList)

			totalSecs = 0
			for tm in timeList:
			    timeParts = [int(s) for s in tm.split(':')]
			    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
			totalSecs, sec = divmod(totalSecs, 60)
			hr, min = divmod(totalSecs, 60)
			print("Total tid: " + cat + " | Vecka " + str(week))
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

	print("Summa kategori v 1-5: " + str(catTime_ADM))
	print("Summa kategori v 1-5: " + str(catTime_WEBB))
	print("Summa kategori v 1-5: " + str(catTime_MEDIA))
	print("Summa kategori v 1-5: " + str(catTime_ITPED))
	print("Summa kategori v 1-5: " + str(catTime_MOTE))
	print("Summa kategori v 1-5: " + str(catTime_UTV))
	print("Summa kategori v 1-5: " + str(catTime_SUP))
	print("Summa totalt veckor 1-5: " + str(timeList_weeks_in_month))

	
	#percList = []

	#catTime = catTime_ADM

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
			#print(l1)
			l2 = str([timeList_weeks_in_month [x]])
			#print(l2)

			totalSecs = 0

			for tm in ([catTime [x]]):
				timeParts = [int(s) for s in tm.split(':')]
				totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
			totalSecs, sec = divmod(totalSecs, 60)
			hr, min = divmod(totalSecs, 60)

			cat_time = (("%d:%02d:%02d") % (hr, min, sec))
			#print("Time category: " + cat_time)

			totalSecs = 0

			for tm in ([timeList_weeks_in_month [x]]):
				timeParts = [int(s) for s in tm.split(':')]
				totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
			totalSecs, sec = divmod(totalSecs, 60)
			hr, min = divmod(totalSecs, 60)

			tot_time = (("%d:%02d:%02d") % (hr, min, sec))
			#print("Time total: " + tot_time)


			hh, mm, ss = map(int, cat_time.split(':'))
			t1 = timedelta(hours=hh, minutes=mm, seconds=ss)
			hh, mm, ss = map(int, tot_time.split(':'))
			t2 = timedelta(hours=hh, minutes=mm, seconds=ss)
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


	html_cat = ('<script> const labels = ["1", "2", "3", "4", "5", "6", "7"]; const NUMBER_CFG = {min: 0, max: 100}; const data = {labels: labels, datasets: [{ label: "Administration", data: [' 
		+ percList_ADM + '], borderColor: "rgb(255, 99, 132)", backgroundColor: "rgb(255, 99, 132)",}, { label: "IT-pedagog", data: [' 
		+ percList_ITPED + '], borderColor: "#7db53f", backgroundColor: "#7db53f",}, { label: "Egen utveckling", data: [' 
		+ percList_UTV + '], borderColor: "#bf2c2c", backgroundColor: "#bf2c2c",}, { label: "Support", data: [' 
		+ percList_SUP + '], borderColor: "#3580dc", backgroundColor: "#3580dc",}, { label: "Möten", data: [' 
		+ percList_MOTE + '], borderColor: "#6d35dc", backgroundColor: "#6d35dc",}, {label: "Webb", data: [' 
		+ percList_WEBB +'], borderColor: "#0dcaf0", backgroundColor: "#0dcaf0",}, {label: "Mediaproduktion", data: [' 
		+ percList_MEDIA + '], borderColor: "#ffc107", backgroundColor: "#ffc107",}]}; const config = {type: "line", data: data, options: {color: "#ffffff", responsive: true, plugins: {legend: {position: "top",}, } }, }; var myChart = new Chart(document.getElementById("myChart30"), config);</script>')

	with open("7weekcats.php", "w") as f2:
			f2.write(html_cat)

	#print("Summa totalt veckor 1-5: " + str(timeList_weeks_in_month))

	timeList_weeks_in_month = str(timeList_weeks_in_month)
	timeList_weeks_in_month = timeList_weeks_in_month.replace(":00","")
	timeList_weeks_in_month = timeList_weeks_in_month.replace(":",".")
	timeList_weeks_in_month = timeList_weeks_in_month.replace("'","")
	timeList_weeks_in_month = timeList_weeks_in_month.replace("[","")
	timeList_weeks_in_month = timeList_weeks_in_month.replace("]","")

	#print(timeList_weeks_in_month)

	html_hours = ('<script> const labels2 = ["1", "2", "3", "4", "5", "6", "7"]; const NUMBER_CFG2 = {min: 0, max: 100}; const data2 = {labels: labels2, datasets: [{ label: "40 TIMMAR", data: [40, 40, 40, 40, 40, 40, 40], borderColor: "rgb(255, 99, 132)", backgroundColor: "rgb(255, 99, 132)", borderDash: [5, 5],}, {label: "ARBETAD TID", data: [' 
		+ timeList_weeks_in_month + '], borderColor: "#ffc107", backgroundColor: "#ffc107",}]}; const config2 = {type: "line", data: data2, options: {color: "#ffffff", responsive: true, plugins: {legend: {position: "top",}, } }, }; var myChart2 = new Chart(document.getElementById("myChart1"), config2);</script>')

	with open("7weekhours.php", "w") as f3:
			f3.write(html_hours)


def timeNow():
	global klNu
	global day
	global date
	global month

	klNu = (t.strftime("%H:%M"))
	year = (t.strftime("%Y"))
	month = (t.strftime("%B"))
	date = (t.strftime("%d"))
	day = (t.strftime("%A"))

	print(klNu)
	print(day)

	styleTime = ''

	with open("time.php", "w") as f1:
		f1.write(styleTime + '<h1 class="clock"><i class="far fa-clock" aria-hidden="true"></i> ' + klNu + '</h1><h4>SENAST UPPDATERAT<br />' + day + ' | ' + date + ' ' + month + ' ' + year + ' | ' + klNu + '</h4>')


def Main():

	while True:

		Calendar()
		removedEvents()
		sumTimeCat()
		Stats7weeks()
		timeNow()
		FileuUploads()
		t.sleep(600)


### MAIN PROGRAM ###
if __name__ == "__main__":
	Main()


