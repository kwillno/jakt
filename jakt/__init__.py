import os
import yaml
import json
import random
from datetime import datetime
from time import time
import click

from .timeslot import timeslot
from .report import JaktReport
from .exceptions import *


class jakt:
    def __init__(self) -> None:
        # TODO: Read from config path and set variables

        self.dataPath = os.path.join(os.path.expanduser("~"), ".jakt")

        self.pathConfig = os.path.join(self.dataPath, "config.yml")
        self.pathCategories = os.path.join(self.dataPath, "categories.yml")
        self.pathProjects = os.path.join(self.dataPath, "projects.json")
        self.pathTimeslots = os.path.join(self.dataPath, "timeslots.json")
        self.pathCurrent = os.path.join(self.dataPath, "current.json")

        # Standard setup for first time use.
        if not os.path.exists(self.dataPath):
        	self.setup()

        with open(self.pathConfig, "r") as f:
            self.config = yaml.safe_load(f)

        # Check if debug mode is enabled
        # If it is, redirect file-operations to subfolder
        if self.config["debug"]:
            self.dataPath = os.path.join(self.dataPath, "debug")

            self.pathCategories = os.path.join(self.dataPath, "categories.yml")
            self.pathProjects = os.path.join(self.dataPath, "projects.json")
            self.pathTimeslots = os.path.join(self.dataPath, "timeslots.json")
            self.pathCurrent = os.path.join(self.dataPath, "current.json")

            if not os.path.exists(self.dataPath):
                self.setup()

    def setup(self) -> None:
        """
        Performs first time setup
        """
        os.mkdir(self.dataPath)

        # Create standard files
        paths = [
            self.pathConfig,
            self.pathCategories,
            self.pathProjects,
            self.pathTimeslots,
        ]

        for path in paths:
            f = open(path, "x")
            f.close()

        # Create barebones config
        config = {
            "remote": False,
            "debug": False,
        }
        with open(self.pathConfig, "a") as f:
            yaml.dump(config, f, default_flow_style=True)

    ## Main working functions
    def start(self, project: str, tags: list[str]) -> dict:
        """
        Adds inputed data into the current file in jakt directory.
        """

        if os.path.exists(self.pathCurrent):
            raise JaktActiveError

        if tags == ():
            tags = ["<no tags>"]

        ts = timeslot(
            ID=self.generateUniqueID(),
            start=round(time()),
            end=None,
            project=project,
            tags=tags
        )

        with open(self.pathCurrent, "w") as f:
            f.write(str(ts.toDictString()))
            f.close()

        return ts

    def stop(self) -> timeslot:
        if not os.path.exists(self.pathCurrent):
            raise JaktNotActiveError

        # Update status from file
        self.status()

        #  Create object to add
        ts = timeslot(
            ID=self.generateUniqueID(),
            start=self.activeTimeslot["start"],
            end=round(time()),
            project=self.activeTimeslot["project"],
            tags=self.activeTimeslot["tags"],
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

        elapsedTime = datetime.fromtimestamp(round(time())) - datetime.fromtimestamp(
            status["start"]
        )
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

    def report(self) -> JaktReport:
        """
        Returns a JaktReport object
        """

        return JaktReport(self)

    def resume(self) -> timeslot:
    	"""
    	Starts new timeslot with same options as previously logged timeslot
    	"""

    	# Get last logged timeslot
    	timeslots = self.getTimeslots()
    	timeslots.reverse()
    	last_ts = timeslots[0]

    	response = self.start(project = last_ts.project, tags = last_ts.tags)

    	return response


    ## Get and put data
    def getConfig(self) -> dict:
        return self.config

    def putConfig(self, config : dict = None) -> None:
        if not config:
            config = self.getConfig()

        with open(self.pathConfig, "w") as f:
            yaml.dump(config, f, default_flow_style=True)

        return


    def getCategories(self) -> list[str]:
        """
        Returns a list of all defined categories
        """
        try:
            with open(self.pathCategories, "r") as f:
                categories = yaml.safe_load(f)
                f.close()

            if type(categories)==type(None):
                categories = []

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

    def getTimeslots(
        self, from_=False, to=False, project=False, tag=False
    ) -> list[timeslot]:
        """
        Returns a list of logged timeslots
        """
        try:
       	    try:
                with open(self.pathTimeslots, "r") as f:
                    timeslots = json.load(f)
                    f.close()
            except json.JSONDecodeError:
                return[]

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

            # Filters by tags if tage are given
            if tag:
                tag_filter = []
                for ts in timeslots:
                    if tag in ts.tags:
                        tag_filter.append(ts)

                timeslots = tag_filter

            return timeslots
        except OSError:
            raise JaktPathError(self.pathTimeslots)

    def getTimeslot(self, queryId: str) -> timeslot:
        timeslots = self.getTimeslots()

        for ts in timeslots:
            if ts.id == queryId:
                return ts

        return False

    def putTimeslots(self, timeslots: list[timeslot]) -> None:
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
    def generateUniqueID(self) -> str:
        timeslots = self.getTimeslots()

        usedIDs = []
        for ts in timeslots:
            usedIDs.append(ts.id)

        ID = f"{random.randrange(16**8):08x}"
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

    ## Import / Export

    def toCSV(self, timeslots):
        """
        Returns list of CSV lineitems for all timeslots. 
        """

        csvLines = []

        header = "id,start,end,project,tags"
        csvLines.append(header)

        for ts in timeslots:
            csvLines.append(ts.toCSV())

        return csvLines


    def export(self, path:str = None):
        """
        Exports all timeslot data to a CSV file
        """
        if path is not None:
            if path[-4:] != ".csv":
                raise JaktPathError("Only CSV files are supported for now. Path must end with '.csv'")

            if path[0] == "/":
                raise JaktPathError("Absolute paths are not supported.")
            else:
                fullPath = os.path.join(os.getcwd(), path)
        else:
            fullPath = os.path.join(self.dataPath, "export.csv")

        timeslots = self.getTimeslots()

        csvItems = self.toCSV(timeslots)

        with open(fullPath, "w") as f:
            for item in csvItems:
                f.write(f"{item}\n")
            f.close()

        return

    def importCSV(self, csv_file):
        pass

