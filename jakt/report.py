from datetime import datetime, timedelta
import click

class JaktReport:
	def __init__(self, jkt):
		#self.categories = jkt.getCategories()
		projects = jkt.getProjects()

		self.data = []
		for i in range(len(projects)):
			project = projects[i]

			projectDuration = timedelta(0)

			tags = jkt.getTags(project=project)

			for j in range(len(tags)):
				timeslots = jkt.getTimeslots(project=project, tag=tags[j])

				tagDuration = timedelta(0)
				for ts in timeslots:
					tagDuration += ts.duration

				tagobj = {
					'tag': tags[j],
					'timeslots': timeslots,
					'time': tagDuration
				}

				tags[j] = tagobj

			# Calculate project duration
			timeslots = jkt.getTimeslots(project=project)
			for ts in timeslots:
				projectDuration += ts.duration

			projectObj = {
				'project': project,
				'tags': tags,
				'time': projectDuration
			}

			self.data.append(projectObj)


	def __str__(self):
		return f"{self.data}"

	def hrDuration(self, td):
		s = str(td).split(':')
		return f"{int(s[0]):02}:{int(s[1]):02}:{int(s[2]):02}"

	def getProjectReport(self, project:str = "") -> list[dict]:
		report = []
		for proj in self.data:
			proj_report = {
				'project': proj['project'],
				'time': self.hrDuration(proj['time'])
			}

			if project:
				if proj['project'] == project:
					report.append(proj_report)
				continue
			report.append(proj_report)

		return report

	def getTagReport(self, project:str  = "") -> list[dict]:
		"""
		Returns a report of all tags for a given project
		"""
		if not project:
			raise JaktInputError

		# Find project that matches given project string
		for proj in self.data:
			if proj["project"] == project:
				selectedProject = proj

		# Generate report
		report = []
		for tg in selectedProject["tags"]:
			tag_report = {
				'tag': tg['tag'],
				'time': self.hrDuration(tg['time'])
			}
			report.append(tag_report)

		return report