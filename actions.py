import json, re
from datetime import timedelta
from datetime import datetime as dt
from utilities import custom_request
from bs4 import BeautifulSoup

class BotActions(object):
	'''   This class will be used for bot action items and other miscellaneous work   '''

	def __init__(self):
		self.cowin_host = 'cdn-api.co-vin.in'
		self.url_calendarByPin = '/api/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date={date}'
		self.url_findByPin = '/api/v2/appointment/sessions/public/findByPin?pincode={pincode}&date={date}'
		self.govIn_host = 'www.mygov.in'
		self.covid_data_url = '/covid-19#statewise-data'
		self.text_template = ("{date}\n"+
								"{min_age}+,D1:{dose1},D2:{dose2},{vaccine},{fee_type}\n"+
								"{center_name}\n"+
								"{center_address}\n"+
								"{district_name}")
		self.situation_template =("Of the total %s cases in %s, there are %s active cases as of now. "+
								"%s patients have been discharged and %s people have been vaccinated. "+
								"Unfortunately we have lost %s people.")
	
	def get_covid_info(self, state_name):
		'''   Return Covid information of state/India   '''
		try:
			data, status = custom_request(self.govIn_host, url=self.covid_data_url)
			soup = BeautifulSoup(data, 'html.parser')

			if state_name.lower() == 'india':
				counts = soup.findAll("span", attrs={"class" : "icount"}, limit=4)
				active,confirmed,discharged,death = counts[0].text,counts[1].text,counts[2].text,counts[3].text
				vaccination = soup.find("div", attrs={"class" : "total-vcount"}).strong.text
			else:
				state_info = soup.find("span", attrs={"class" : "st_name"}, 
											text=re.compile('\\b'+state_name+'\\b', re.IGNORECASE))
				state_name = state_info.text
				state_counts = state_info.find_next_sibling("div", attrs={"class" : "st_all_counts"})
				confirmed = state_counts.find("div", attrs={"class" : "tick-confirmed"}).small.text
				active = state_counts.find("div", attrs={"class" : "tick-active"}).small.text
				discharged = state_counts.find("div", attrs={"class" : "tick-discharged"}).small.text
				death = state_counts.find("div", attrs={"class" : "tick-death"}).small.text
				vaccination = state_counts.find("div", attrs={"class" : "tick-total-vaccine"}).small.text

			return self.situation_template %(confirmed,state_name,active,discharged,vaccination,death)

		except Exception as ex:
			print(ex)
			return "Error"


	def get_vaccine_slots(self, dateObj, pincode):
		'''   Returns vaccine slots information   '''

		date_str = dt.strftime(dateObj, '%d-%m-%Y')
		data, status = custom_request(self.cowin_host, 
							self.url_findByPin.format(pincode=pincode, date=date_str))
		vaccine_slots = {'match':[], 'full':[], 'error':False}
		
		try:
			# First we check if any slot is available for the exact date and pincode
			if data is not None:
				data = json.loads(data, encoding='utf-8')
				for center in data['sessions']:
					if center['available_capacity'] > 0:
						vslot_info = self.text_template.format(date=center.get('date',''), 
										min_age=center.get('min_age_limit','NA'),
										dose1=center.get('available_capacity_dose1','NA'),
										dose2=center.get('available_capacity_dose2','NA'),
										vaccine=center.get('vaccine','NA'), 
										fee_type=center.get('fee_type','NA'),
										center_name=center.get('name', 'NA'), 
										center_address=center.get('address', 'NA'),
										district_name=center.get('district_name', 'NA'))
						vaccine_slots['match'].append(vslot_info)
			
			if len(vaccine_slots['match']) > 0:
				return vaccine_slots

			# Now we get the full calendar on that pincode
			from_dates = [dt.strftime(dt.today(), '%d-%m-%Y'), dt.strftime(dt.today()+timedelta(days=7), '%d-%m-%Y')]
			for fdate in from_dates:
				data, status = custom_request(self.cowin_host, 
									self.url_calendarByPin.format(pincode=pincode, date=fdate))
				if data is not None:
					data = json.loads(data, encoding='utf-8')
					for center in data['centers']:
						for session in center['sessions']:
							if session['available_capacity'] > 0:
								vslot_info = self.text_template.format(date=session.get('date',''), 
											min_age=session.get('min_age_limit','NA'),
											dose1=session.get('available_capacity_dose1','NA'),
											dose2=session.get('available_capacity_dose2','NA'),
											vaccine=session.get('vaccine','NA'), 
											fee_type=center.get('fee_type','NA'),
											center_name=center.get('name', 'NA'), 
											center_address=center.get('address', 'NA'),
											district_name=center.get('district_name', 'NA'))
								vaccine_slots['full'].append(vslot_info)

			return vaccine_slots
		except:
			vaccine_slots['error']=True
			return vaccine_slots



if __name__ == '__main__':
	botaction = BotActions()
	# slots = botaction.get_vaccine_slots(dt.strptime('2021-06-30','%Y-%m-%d').date(), '700084')
	# if len(slots['match']) > 0:
	# 	print("Yeyeye..! We got a slot")
	# 	for slot in slots['match']:
	# 		print(slot)
	# if len(slots['full']) > 0:
	# 	print("Here is the full calendar")
	# 	for slot in slots['full']:
	# 		print(slot)
	# print(botaction.get_covid_info('pradesh'))
