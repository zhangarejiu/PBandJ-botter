import time
#import filereader
from triangular import run_triangular
from "../creds/handle_creds.py" import decrypt

# TO DO:
# LOG FILES

def open_logs():
	"""Function for creating log files, return file names"""
	return log, action_log, error_log


def update_logs(event, log, action_log, error_log):
	"""update the logs to reflect relevant events"""
	if event["type"] == "error":
		#Update the error log file
	else:
		# event["type"] == "action"
		#Update action file


class Bot():
	"""Bot class instance. Specify strategy at construction."""

	def __init__(self, strategy):
		"""Currently available strategies: triangular"""
		self.strategy = strategy
		self.start_time = time.time()
		self.log, self.action_log, self.error_log = open_logs() #NEED TO CREATE THIS FUNCTION

	def import_credentials(password, cred_file):
		"""Imports the credentials used for each exchange"""
		self.exchanges = decrypt(password, cred_file)

	def run_bot(currency, run_time):
		"""Specify algorithm to use with bot"""
		if self.strategy == "triangular":
			run_triangular(self, currency, run_time)

	def update_log(event)
		update_logs(event, self.log, self.action_log, self.error_log)
		





