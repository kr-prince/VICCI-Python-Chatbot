import re
import http.client
import parsedatetime
from pytz import timezone
from datetime import datetime as dt
from fuzzywuzzy import process, fuzz

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'

def custom_request(host, url, method='GET'):
	'''   Our own custom request function   '''
	data, status = None, None
	headers = {
			'Content-Type': 'application/json',
			'Cache-Control': 'no-cache',
			'User-Agent': user_agent 
		}
	
	try:
		conn = http.client.HTTPSConnection(host)
		conn.request(method, url=url, headers=headers)
		resp = conn.getresponse()
		assert (resp.status == 200)
		data = resp.read()
		status = resp.reason
	except Exception as ex:
		data = None
		status = str(ex)
	return data, status


def extract_state_name(query):
	'''   Extract the state name from sentence in fuzzy match way   '''

	try:
		state_names=[]
		with open('./data/state_names.txt', 'r', encoding='utf-8-sig') as file:
			state_names = [state.strip() for state in file.readlines()]+['India']
		state, score = process.extractOne(query,state_names,scorer=fuzz.token_set_ratio)
		if score < 60:
			# In case of any error or low in confidence return None
			state, score = None, 0
	except Exception as ex:
		state = None
	return state


def extract_pin_code(query):
	'''   Extract the pincode from query   '''

	pincode = None
	try:
		match = re.search(r'\b[1-9][0-9]{5}\b', query)
		# print(match)
		if match is not None:
			pincode = match.group(0)
	except:
		pass
	return pincode


def extract_date(query):
	'''   Extract the date from query   '''

	cal, dateObj, parse_status = parsedatetime.Calendar(), None, 0
	try:
		dateObj, parse_status = cal.parseDT(query)
		if parse_status == 0:
			# parse_status is 0 for failure
			dateObj = None
		else:
			dateObj = dateObj.date()
	except:
		pass
	return dateObj

def get_date_difference(date1, date2):
	'''   get the difference in dates in days   '''
	
	if date1=='today':
		date1 = dt.today().date()
	delta = date2 - date1
	return delta.days

