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

class JaktPathError(JaktError, path):
	self.path = path


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
			with open(self.pathTimeslots, 'a') as f:
				yaml.dump([], f, default_flow_style=False)



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

		self.status()
		self.add()

		# Removes timeslot data in current timeslot
		os.remove(self.pathCurrent)

		return self.activeTimeslot



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

		self.activeTimeslot = status

		return status


	def add(self):
		"""
		Adds new timeslot from. 
		TODO: Implement add for known data.
		"""
		# Update 
		self.status()

		#  Create object to append
		ts = {
			"id": self.generateUniqueID(), 
			"start": self.activeTimeslot["start"],
			"end": round(time()),
			"project": self.activeTimeslot["project"],
			"tags": self.activeTimeslot["tags"]
		}

		# Find all logged timeslots
		timeslots = self.getTimeslots()

		# Append new timeslot to list
		timeslots.append(ts)

		# Write all timeslots, including newly added to file
		self.putTimeslots(timeslots)

	def report(self):
		pass


	## Get and put data
	def getCategories(self):
		pass

	def getProjects(self):
		pass

	def getTags(self):
		pass

	def getTimeslots(self) -> list[dict]:
		"""
		Returns a list of all logged timeslots
		"""
		try:
			with open(self.pathTimeslots, "r") as f:
				timeslots = json.load(f)
				f.close()

			return timeslots
		except OSError:
			raise JaktPathError(self.pathTimeslots)

	def putTimeslots(self, timeslots: list[dict]):
		try:
			with open(self.pathTimeslots, "w") as f:
				json.dump(timeslots, f)
				f.close()
		except OSError:
			raise JaktPathError(self.pathTimeslots)

	## Helper functions
	def generateUniqueID(self):
		timeslots = self.getTimeslots()

		usedIDs = []
		for ts in timeslots:
			usedIDs.append(ts["id"])

		ID = '%08x' % random.randrange(16**8)
		if ID not in usedIDs:
			return ID
		else:
			return self.generateUniqueID()


	## Remote syncronization
	def fetch(self):
		pass

	def pull(self):
		pass

	def push(self):
		pass

