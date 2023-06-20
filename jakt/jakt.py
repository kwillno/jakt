import os
import yaml
import json
import random
from datetime import datetime, timedelta
from time import time
import click

# Selfdefined Errors
class JaktError(Exception):
    pass


class JaktActiveError(JaktError):
	pass


class JaktNotActiveError(JaktError):
	pass


# Main class
class _jakt:
	def __init__(self):
		# TODO: Set up config
		# TODO: Read from config path and set variables

		self.dataPath = os.path.join(os.path.expanduser('~'), ".jakt")
		self.pathConfig = os.path.join(self.dataPath, "config.yml")
		self.pathCategories = os.path.join(self.dataPath, "categories.json")
		self.pathProjects = os.path.join(self.dataPath, "projects.json")
		self.pathTimeslots = os.path.join(self.dataPath, "timeslots.json")
		self.pathCurrent = os.path.join(self.dataPath, "current.json")

		# Standard setup for first time use. 
		if not os.path.exists(self.dataPath):
			os.mkdir(self.dataPath)

			# Create standard files
			paths = [self.pathConfig,self.pathCategories, self.pathProjects, self.pathTimeslots]

			for path in paths:
				# Create standard config
				f = open(path, "x")
				f.close()

			standardConfig = {
				"Remote": False
			}
			with open(self.pathConfig, 'a') as f:
				yaml.dump(standardConfig, f, default_flow_style=False)



	## Main working functions
	def start(self, project: str, tags: list[str]) -> dict:
		"""
		Adds inputed data into the current file in jakt directory.
		"""

		if os.path.exists(self.pathCurrent):
			raise JaktActiveError

		timeslot = {
			"start": round(time()),
			"project": project,
			"tags": tags
		}

		timeslotJSON = json.dumps(timeslot, indent = 4)

		with open(self.pathCurrent, "w") as f:
			f.write(timeslotJSON)
			f.close()

		return timeslot
		

	def stop(self) -> dict:
		if not os.path.exists(self.pathCurrent):
			raise JaktNotActiveError

		# Takes data from current timeslot
		#with open(self.pathCurrent, "r") as f:
		#	timeslot = json.load(f)
		#	f.close()
		timeslot = self.status()

		# Add new properties to timeslot
		ts_id = '%08x' % random.randrange(16**8)
		# TODO: Check if id already exists

		timeslot["id"] = ts_id
		timeslot["end"] = round(time())

		# Add new timeslot to log
		with open(self.pathTimeslots, "a") as f:
			json.dump(timeslot, f)

		# Removes timeslot data in current timeslot
		os.remove(self.pathCurrent)

		return timeslot



	def status(self) -> dict:
		if not os.path.exists(self.pathCurrent):
			raise JaktNotActiveError

		with open(self.pathCurrent, "r") as f:
			status = json.load(f)
			f.close()

		elapsedTime = datetime.fromtimestamp(round(time())) - datetime.fromtimestamp(status["start"])
		status["elapsed"] = elapsedTime.seconds

		hours, remainder = divmod(elapsedTime.seconds, 3600)
		minutes, seconds = divmod(remainder, 60)

		status["elapsedHour"] = hours
		if seconds > 30:
			status["elapsedMin"] = minutes + 1
		else:
			status["elapsedMin"] = minutes

		# TODO: Elapsed time

		return status


	def add(self):
		pass

	def report(self):
		pass


	## Get data
	def getCategories(self):
		pass

	def getProjects(self):
		pass

	def getTags(self):
		pass

	def getTimeslots(self):
		pass


	## Remote syncronization
	def fetch(self):
		pass

	def pull(self):
		pass

	def push(self):
		pass

