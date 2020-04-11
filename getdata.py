import requests, json, arrow, hashlib, urllib, datetime
from secret import	NS_URL, NS_SECRET,	CLIENT_ID, CLIENT_SECRET,REFRESH_TOKEN
import csv
import glob
import os
import xml.etree.ElementTree
from datetime import datetime, timedelta
import calendar
import time
import argparse
import sys
from google.auth.transport.requests import AuthorizedSession
from  oauth2client import client

NS_AUTHOR = "Google Fit"
TIMEZONE = "Europe/Berlin"
MIN_DURATION_SEC = 600

ACCESS_TOKEN = ""

def google_login():
	GOOGLE_REVOKE_URI = "urn:ietf:wg:oauth:2.0:oob"
	auth_endpoint = 'https://accounts.google.com/o/oauth2/v2/auth'
	token_endpoint ='https://www.googleapis.com/oauth2/v4/token'
	string = 'client_secret=' + CLIENT_SECRET + '&grant_type=refresh_token&refresh_token=' + REFRESH_TOKEN + '&client_id=' +CLIENT_ID

	scope = "https://www.googleapis.com/auth/fitness.activity.read"

	result = requests.post('https://www.googleapis.com/oauth2/v4/token', string, headers={
		'Host': 'www.googleapis.com',
		'Content-length': str(len(string)),
		'content-type': 'application/x-www-form-urlencoded',
		'user-agent': GOOGLE_REVOKE_URI
	})

	result = result.json()
	global ACCESS_TOKEN
	ACCESS_TOKEN = result["access_token"]

	return

def request_gfit_getAggregate(lastEntryTime):
	#auth_code = login.json()['token']
	print("Loading entries...")

	if lastEntryTime == None:
		lastEntryTime = datetime.now() - timedelta(days= 1)
	timeStart = date_to_ms(lastEntryTime)
	timeEnd =	date_to_ms(datetime.now())
	entries = requests.post('https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate', 
		#cookies=login.cookies, 
		headers={
			'origin': 'https://www.googleapis.com',
			'authorization': 'Bearer '+ACCESS_TOKEN
		}, json={
  			"startTimeMillis": timeStart,
  			"endTimeMillis":   timeEnd,
  			"aggregateBy": [
   				 {
    			"dataTypeName": "com.google.calories.expended",
     			 #"dataSourceId": "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
				"dataSourceId": "derived:com.google.calories.expended:com.google.android.gms:from_activities"
    			}
  			],
  			"filteredDataQualityStandard": [],
 			 "bucketByTime": {
   			 "durationMillis": 60 * 60 * 1000, #24 * 60 * 60 * 1000
    		#"period": {
      		#"type": "day"
    		#}
  		}
		})
	return entries.json()

def read_gfitAggregate(entries):
	out_activity = []
	for bucket in entries['bucket']:
		duration = 60 * 60  / 2
		start = float(bucket['startTimeMillis'])/int(1e3)
		middle = start + duration
		for dataset in bucket['dataset']:
			for point in dataset['point']:
				for value in point['value']:
					if 'intVal' in value:
						cal = value['intVal']
					elif 'fpVal' in value:
						cal = value['fpVal']
					date = datetime.fromtimestamp(middle)
					middle = arrow.get(middle).to("Europe/Berlin")
					print("Got Data for day: ", str(date.strftime("%A %d. %B %Y")), " and time " , date.strftime("%H:%M:%S"), ": " ,str(cal) )
					out_activity.append({
						"date": middle.timestamp * 1000,
						"created_at": middle.format(),
						"device": "Google Fit Calories Aggregate",
						"eventType": "Exercise",
						"enteredBy": NS_AUTHOR,
						"calories" : cal
						})
					if len(out_activity) > 100:
						upload_nightscout_activity(out_activity)
						out_activity= []
	upload_nightscout_activity(out_activity)
	return

def request_gfit_getStream(dataStreamId,lastEntryTime):
	#auth_code = login.json()['token']
	print("Loading entries...")
	#timeStart = date_to_ms(datetime.now() + timedelta(days=-7)) * int(1e6)
	if lastEntryTime == None:
		lastEntryTime = datetime.now() - timedelta(days= 1)
		print("Date of last gfit is not availabe. Fallback: take last day: ", str(lastEntryTime))
	timeStart = int((lastEntryTime.timestamp()+1) * int(1e9))
	timeEnd =	date_to_ms(datetime.now() )* int(1e6)
	#dataStreamId= "derived:com.google.calories.expended:com.google.android.gms:from_activities"
	url = "https://www.googleapis.com/fitness/v1/users/me/dataSources/" + dataStreamId + "/datasets/" + str(timeStart) + "-" + str(timeEnd)
	entries = requests.get(url, 
		#cookies=login.cookies, 
		headers={
			'origin': 'https://www.googleapis.com',
			'authorization': 'Bearer '+ACCESS_TOKEN
		})
	return entries.json()

def read_gfitStream(entries):
	out_treatments = []
	author = NS_AUTHOR
	for point in entries['point']:
		start = float(point['startTimeNanos'])/int(1e9)
		end = float(point['endTimeNanos'])/int(1e9)
		durationSec = end - start
		for value in point['value']:
			if 'intVal' in value:
				cal = value['intVal']
			elif 'fpVal' in value:
				cal = value['fpVal']
			# dateStart = datetime.fromtimestamp(start)
			if durationSec > MIN_DURATION_SEC and cal != 3 and cal != 0:
				dateStart = arrow.get(start).to(TIMEZONE)
				created_at = dateStart.format('YYYY-MM-DDTHH:mm:ssZ')
				sport = getActivity(cal)
				print("Got Activity: ",sport ,cal,	str(dateStart.format()), str(int(durationSec/60)) )
				out_treatments.append({
						"date": dateStart.timestamp * 1000,
						"created_at": created_at,
						"device": "Google Fit REST",
						"eventType": "Exercise",
						"enteredBy": author,
						"notes":sport,
						"duration":str(durationSec/60)
						})
				if len(out_treatments) > 100:
					upload_nightscout_treatments(out_treatments)
					out_treatments= []

	upload_nightscout_treatments(out_treatments)		
	return

def to_mgdl(mmol):
	return round(mmol*18)

def getActivity(type):
	# see https://developers.google.com/fit/rest/v1/reference/activity-types
	activity = 'Sport'
	if type == 0:
		activity = "In Vehicle"
	if type == 1:
		activity = "Biking"
	if type == 2:
		activity = "On foot"
	if type == 3: 
		activity = "Still"
	if type == 4:
		activity = "Unknown "
	if type == 5:
		activity = "Tilting "
	#if type == 6:
		#		activity = "??"
	if type == 7:
		activity = "Walking"
	if type == 8:
		activity = "Running"
	if type == 35:
		activity = "Hiking"
	return activity

def date_to_ms(ts):
	"""
	Takes a datetime object and returns POSIX UTC in milisecons
	"""
	return calendar.timegm(ts.utctimetuple()) * int(1e3)

def upload_nightscout_treatments(ns_format):
	for ns in ns_format:
		upload = requests.post(NS_URL + 'api/v1/treatments?api_secret=' + NS_SECRET, json=ns, headers={
			'Accept': 'application/json',
			'Content-Type': 'application/json',
			'api-secret': hashlib.sha1(NS_SECRET.encode()).hexdigest()
		})
		print("Nightscout upload status:", upload.status_code, upload.text)

def upload_nightscout_activity(ns_format):
    for ns in ns_format:
        upload = requests.post(NS_URL + 'api/v1/activity?api_secret=' + NS_SECRET, json=ns, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'api-secret': hashlib.sha1(NS_SECRET.encode()).hexdigest()
        })
        print("Nightscout upload status:", upload.status_code, upload.text)
		
def get_last_nightscout():
	#last = requests.get(NS_URL + 'api/v1/treatments?count=1&find[eventType]='+urllib.parse.quote('Exercise'), headers={
	last = requests.get(NS_URL + 'api/v1/treatments?count=1&find[enteredBy]='+urllib.parse.quote(NS_AUTHOR), headers={
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'api-secret': hashlib.sha1(NS_SECRET.encode()).hexdigest()
	})
	if last.status_code == 200:
		js = last.json()
		if len(js) > 0:
			duration = 0
			if 'duration' in js[0]:
				duration = js[0]['duration']
			return arrow.get(js[0]['created_at']).datetime + timedelta(minutes=duration)

def main():
	print("Getting data...", datetime.now())

	ns_last = get_last_nightscout()

	#entries = get_entries_from_libre_export()

	#treatments = get_entries_from_googlefit_tcx()

	#upload_nightscout_entries(entries)
	#upload_nightscout_treatments(treatments)
	#upload_nightscout_activity(activity)
	google_login()

	
	dataStreamId = "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
	dataStreamId= "derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments"

	print("Reading Data for", dataStreamId)
	entries =	request_gfit_getStream(dataStreamId,ns_last)
	read_gfitStream(entries)

	#dataStreamId="derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes"
	#dataStreamId="derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
	entries = request_gfit_getAggregate(ns_last)
	read_gfitAggregate(entries)
	
	print("Got Data for days: ", len(entries))


if __name__ == '__main__':
	main()
