from datetime import datetime

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

	def __str__(self):
		return f"ts: {self.id} {self.project} {self.tags} {self.start_dt.strftime('%d-%m-%y %H:%M')} - {self.end_dt.strftime('%H:%M')}"


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
