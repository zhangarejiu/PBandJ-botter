import time


def get_val(exchange, currency):
	"""Retrieves current valuation for a given currency"""

def check_diff(exchanges, currency):
	"""Checks the differences between prices on each exchange and returns the min and max"""
	vals  = {}
	for i in range(len(exchanges)):
		try:
			val = get_val(exchanges[i], currency)
			vals[exchanges[i]] = val
		except:
			### Would be good to build in logging here
			print("unable to get value for " + currency + " from " + exchanges[i])


	#return the min and max values
	return {'min': min(), 'max': ,'difference':}


def execute_trade(exchanges, trade, currency, threshold, amount, timeout=100):

	if trade['difference'] > threshold:

		#make trade and cashout
		#will have to figure out how to be conservative with $$$ used
		exchanges[trade['min']].send(exchanges[trade['max']], amount, currency)

		#Put bound on transaction time, then cancel
		clock = time.time()

		while exchanges[trade['max']].check_transaction() != True and time.time()-clock>timeout:
			sleep(5)

		if exchanges[trade['max']].check_transaction() == True:
			# $$$ cash out
			exchanges[trade['max']].cashout(amount, currency)


	"""exchanges is an object with auth creds associated"""
	"""Trade is a dict with max, min exchange val"""
	




def run_triangular(bot, currency, run_time):
	"""Run the triangular arbitrage
	ARGS: bot - bot object from bot.py
	      currency - str 
	      run_time - int number of seconds to run bot
	"""
	start_time = time.time()
	while time.time() < start_time + run_time:
		event = {}
		trade = check_diff(self.exchanges, currency)

#USE TRY/EXCEPT FOR THE ERROR LOGGING FOR THE TRADE
		result = execute_trade(self.exchanges, trade, currency)

		bot.update_log(event)








