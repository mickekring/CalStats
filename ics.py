from datetime import date, datetime, timedelta, timezone
import icalendar
from rrule_patched import *

def get_events_from_ics(ics_string, window_start, window_end):
    
    events = []

    def append_event(e):

        if e['startdt'] > window_end:
            return
        if e['enddt']:
            if e['enddt'] < window_start:
                return

        events.append(e)

    def get_recurrent_datetimes(recur_rule, start, exclusions):
        rules = rruleset()
        first_rule = rrulestr(recur_rule, dtstart=start)
        rules.rrule(first_rule)
        if not isinstance(exclusions, list):
            exclusions = [exclusions]

        for xdt in exclusions:
            try:
                rules.exdate(xdt.dt)
            except AttributeError:
                pass

        dates = []

       
        for d in rules.between(window_start, window_end):
            dates.append(d)
        return dates



    cal = filter(lambda c: c.name == 'VEVENT',
        icalendar.Calendar.from_ical(ics_string).walk()
        )

    def date_to_datetime(d):
        return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


    for vevent in cal:
        uid = str(vevent.get('uid'))
        summary = str(vevent.get('summary'))
        description = str(vevent.get('description'))
        location = str(vevent.get('location'))
        rawstartdt = vevent.get('dtstart').dt
        rawenddt = vevent.get('dtend').dt #fix från enddt till dtend
        allday = False
        if not isinstance(rawstartdt, datetime):
            allday = True
            startdt = date_to_datetime(rawstartdt)
            if rawenddt:
                enddt = date_to_datetime(rawenddt)
        else:
            startdt = rawstartdt
            enddt = rawenddt

        exdate = vevent.get('exdate')
        if vevent.get('rrule'):
            reoccur = vevent.get('rrule').to_ical().decode('utf-8')
            for d in get_recurrent_datetimes(reoccur, startdt, exdate):
                new_e = {
                    'uid': uid,
                    'startdt': d,      
                    'allday': allday,                  
                    'summary': summary,
                    'desc': description,
                    'loc': location
                    }
                if enddt:
                    new_e['enddt'] = d + (enddt-startdt)                        
                append_event(new_e)
        else:
            append_event({
                'uid': uid,
                'startdt': startdt,
                'enddt': enddt,
                'allday': allday,
                'summary': summary,
                'desc': description,
                'loc': location
                })
    events.sort(key=lambda e: e['startdt'])
    return events
