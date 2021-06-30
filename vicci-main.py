import os
from flask import Flask, render_template, request, jsonify

import utilities as ut
from botmodel import BotModel
from actions import BotActions


app = Flask(__name__)


class VicciBot(object):
	'''   This is the main bot engine class   '''

	def __init__(self):
		self.botmodel = BotModel()
		self.botmodel.initialize()
		self.botactions = BotActions()

		# define entities and context
		self.context_history = None
		self.entities = {'pincode': None, 'date':None, 'state':None}


	def handle_vaccination(self,pincode, dateObj):
		'''   Just to handle the vaccination part after validating the required entities   '''

		# Update the enities and serve the user, or ask for any other entity if missed
		resp = []
		if pincode is not None:
			self.entities['pincode'] = pincode 
		if dateObj is not None:
			days = ut.get_date_difference('today', dateObj)
			if days < 0:
				resp.append("You are asking for a past date.")
			elif days > 13:
				resp.append("Vaccination calendar is only available for 13 days.")
			else:
				self.entities['date'] = dateObj
		
		if self.entities['pincode'] is None and self.entities['date'] is None:
			resp.append("What is your area pincode and favoured date?")
		elif self.entities['pincode'] is None:
			resp.append("What is your area pincode?")
		elif self.entities['date'] is None:
			resp.append("What is your favoured date?")
		else:
			vaccine_slots = self.botactions.get_vaccine_slots(self.entities['date'], self.entities['pincode'])
			served = False
			if vaccine_slots['error'] is True:
				resp.extend(["Sorry :( Some error occurred while checking vaccination calendar."])
				served = True
			elif len(vaccine_slots['match']) > 0:
				resp.append("Yey.! You can get a free slot.")
				resp.extend(vaccine_slots['match'])
				served = True
			elif len(vaccine_slots['full']) > 0:
				resp.append("You requested date is not available. Please check the full calendar.")
				resp.extend(vaccine_slots['full'])
				served = True
			else:
				resp.append("Sorry :( Looks like there is no available slot for next 2 weeks as of now.")
				served = True

			if served:
				# vaccination has been handled now we can clear the context
				self.context_history = None
				self.entities = dict.fromkeys(self.entities, None)

		return resp

	def response(self, user_query):
		user_query = user_query.strip().lower()
		bot_responses, served = [], False

		if self.context_history == 'vaccination_slot':
			# Lets check if this query is a follow up and bot is asking for pincode/date
			pincode = ut.extract_pin_code(user_query)
			dateObj = ut.extract_date(user_query)
			
			if pincode is None and dateObj is None:
				# If both the entities are empty that means user has dropped that context
				self.context_history = None
				self.entities = dict.fromkeys(self.entities, None)
				bot_responses.append("I did not get date or pincode in your input. "+
								"Aborting vaccine slots checking.")
			else:
				bot_responses.extend(self.handle_vaccination(pincode, dateObj))
				served = True
				
		if self.context_history != 'vaccination_slot' and not served:
			tag, conf, resp = self.botmodel.response(user_query)

			if conf < 0.3:
				# Too low confidence of the intent classifier 
				bot_responses.append("Sorry. I did not understand your query.")

			else:
				if tag=='covid_numbers':
					# bot_responses.clear()
					self.entities['state']= ut.extract_state_name(user_query)
					if self.entities['state'] is None:
						# if we could not get the state name with high confidence or some 
						# error occurred we display the info for India
						self.entities['state'] = 'India'
						bot_responses.append("Did not find any state name, fetching the data for India.")
					
					covid_info = self.botactions.get_covid_info(self.entities['state'])
					if covid_info == 'Error':
						bot_responses.append("Sorry :( Some error occurred while fetching Covid data.")
					else:
						bot_responses.append(covid_info)

				elif tag=='vaccination_slot':
					# check for entities 
					pincode = ut.extract_pin_code(user_query)
					dateObj = ut.extract_date(user_query)
					bot_responses.extend(self.handle_vaccination(pincode, dateObj))

				else:
					bot_responses.extend(resp)

			self.context_history = tag

		return jsonify(bot_responses)


vbot = VicciBot()

def lastUpdateTime(folder):
	# This function returns the latest last updated timestamp of all the static files 
	return str(max(os.path.getmtime(os.path.join(root_path, file)) \
		for root_path, dirs, files in os.walk(folder) \
			for file in files))

@app.route("/")
def home():
    return render_template("home.html", last_updated=lastUpdateTime('static/'))

@app.route("/get")
def get_bot_response():    
    user_query = request.args.get('user_query')    
    return vbot.response(user_query)

if __name__=='__main__':
	app.run(debug=False)
	