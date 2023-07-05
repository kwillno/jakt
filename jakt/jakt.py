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

class JaktPathError(JaktError):

	def __init__(self, path):
		self.path = path


class timeslot:
	def __init__(self, ID: str, start: int, end: int, project: str, tags: list[str]):
		self.id = ID

		self.start = start
		self.end = end
		self.start_dt = datetime.fromtimestamp(self.start)
		self.end_dt = datetime.fromtimestamp(self.end)

		self.project = project
		self.tags = tags

		# Calculate duration
		start = datetime.fromtimestamp(self.start)
		end = datetime.fromtimestamp(self.end)
		self.duration = end - start

	@classmethod
	def from_json(cls, json_obj: dict):
		return cls( ID=json_obj['id'], start=json_obj['start'], end=json_obj['end'], project=json_obj['project'], tags=json_obj['tags'])

	def toDict(self) -> dict:
		obj = {
			'id': self.id,
			'start': self.start,
			'end': self.end,
			'project': self.project,
			'tags': self.tags,
		}

		return obj

	def getDurationHR(self):
		"""
		Return the data needed to display Human Readale duration
		"""
		hh, remainder = divmod(int(self.duration.total_seconds()), 3600)
		mm, ss = divmod(remainder, 60)

		M = mm
		if ss > 30:
			M = mm + 1

		return {'hh':hh, 'H': hh, "mm": mm, 'M': M, "ss": ss}


class jakt_report:
	def __init__(self, jkt):
		#self.categories = jkt.getCategories()
		self.projects = jkt.getProjects()

		for project in self.projects:
			pass
			

	def __str__(self):
		return f"{self.projects}"


# Main class
class _jakt:
	def __init__(self):
		# TODO: Set up config
		# TODO: Read from config path and set variables

		self.dataPath = os.path.join(os.path.expanduser('~'), ".jakt")
		self.pathConfig = os.path.join(self.dataPath, "config.yml")
		self.pathCategories = os.path.join(self.dataPath, "categories.yml")
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
		else:
			# TODO: Set up config-loading
			pass


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
		

	def stop(self) -> timeslot:
		if not os.path.exists(self.pathCurrent):
			raise JaktNotActiveError

		# Update status from file
		self.status()

		#  Create object to add
		ts = timeslot(
			ID = self.generateUniqueID(), 
			start = self.activeTimeslot["start"],
			end = round(time()),
			project = self.activeTimeslot["project"],
			tags = self.activeTimeslot["tags"]
		)

		# Add object to timeslots
		ts_added = self.add(ts)

		# Removes timeslot data in current timeslot
		os.remove(self.pathCurrent)

		return ts_added



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


	def add(self, ts: timeslot) -> timeslot:
		"""
		Adds new timeslot from. 
		TODO: Implement add for known data.
		"""

		# Find all logged timeslots
		timeslots = self.getTimeslots()

		# Append new timeslot to list
		timeslots.append(ts)

		# Write all timeslots, including newly added to file
		self.putTimeslots(timeslots)

		return ts

	def report(self) -> jakt_report:
		"""
		Returns a jakt_report object containg report info
		"""

		rep = jakt_report(self)

		return rep


	## Get and put data
	def getCategories(self) -> list[str]:
		"""
		Returns a list of all defined categories
		"""
		try:
			with open(self.pathCategories, "r") as f:
				categories = yaml.safe_load(f)
				f.close()

			return categories
		except OSError:
			raise JaktPathError(self.pathCategories)

	def getProjects(self) -> list[str]:
		"""
		Returns list of all projects
		"""
		timeslots = self.getTimeslots()

		projects = []
		for i in range(len(timeslots)):
			if timeslots[i].project not in projects:
				projects.append(timeslots[i].project)

		return projects

	def getTags(self, project: str = None) -> list[str]:
		"""
		Returns a list of all used tags. 

		If project is given only tags for the matching project are given.
		"""
		timeslots = self.getTimeslots()

		tags = []
		for i in range(len(timeslots)):
			if project and not (project == timeslots[i].project):
				continue

			currentTags = timeslots[i].tags

			for j in range(len(currentTags)):

				if currentTags[j] not in tags:
					tags.append(currentTags[j])

		return tags


	def getTimeslots(self, from_ = False, to = False, project = False, tag = False) -> list[timeslot]:
		"""
		Returns a list of logged timeslots
		"""
		try:
			with open(self.pathTimeslots, "r") as f:
				timeslots = json.load(f)
				f.close()

			# Create timeslot instances
			for i in range(len(timeslots)):
				timeslots[i] = timeslot.from_json(timeslots[i])


			# TODO: Implement filtering with to and from_
			if to and from_:
				# Remove timeslots that do not match
				pass


			# Filters by project if project is given
			if project:
				project_filter = []
				for ts in timeslots:
					if ts.project == project:
						project_filter.append(ts)

				timeslots = project_filter

			return timeslots
		except OSError:
			raise JaktPathError(self.pathTimeslots)

	def getTimeslot(self, queryId: str) -> timeslot:
		timeslots = self.getTimeslots()

		for ts in timeslots:
			if ts.id == queryId:
				return ts

		return False

	def putTimeslots(self, timeslots: list[timeslot]):
		obj_list = []

		for ts in timeslots:
			obj_list.append(ts.toDict())

		try:
			with open(self.pathTimeslots, "w") as f:
				json.dump(obj_list, f)
				f.close()
		except OSError:
			raise JaktPathError(self.pathTimeslots)

	## Helper functions
	def generateUniqueID(self):
		timeslots = self.getTimeslots()

		usedIDs = []
		for ts in timeslots:
			usedIDs.append(ts.id)

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


