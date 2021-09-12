import json

from datetime import datetime, timedelta, date
from time import time


datas = json.load(open("datas/colloscope.json", "r"))


DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]


def get_events_of_the_day(day:datetime.date,grp:int) -> list:
	"""Return a list of events of the day `day`od group `grp`

	Args:
		day (datetime.date): The day
		grp (int): The group
    
	Returns:
		[list]: A list of events  
	"""    
	monday = day - timedelta(days = day.weekday())
	column_index = datas["mondays"].index(monday.strftime("%d/%m/%Y")) 

	events = []
	for line in datas["planning"]:
		if line["grps"][column_index] == int(grp) and line["timedelta"]["days"] == day.weekday():
			events.append(line)

	events.sort(key= lambda line : timedelta(**line["timedelta"]))
	
	return events