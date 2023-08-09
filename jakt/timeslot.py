from datetime import datetime
import json


class timeslot:
    def __init__(self, ID: str, start: int, end: int, project: str, tags: list[str]):
        self.id = ID

        self.start = start
        self.end = end
        self.start_dt = datetime.fromtimestamp(self.start)
        if end:
            self.end_dt = datetime.fromtimestamp(self.end)

            start = datetime.fromtimestamp(self.start)
            end = datetime.fromtimestamp(self.end)
            self.duration = end - start

        else:
            self.end_dt = None
            self.duration = None

        self.project = project
        self.tags = tags
        

    def __str__(self):
        return f"ts: {self.id} {self.project} {self.tags} {self.start_dt.strftime('%d-%m-%y %H:%M')} - {self.end_dt.strftime('%H:%M')}"

    @classmethod
    def from_json(cls, json_obj: dict):
        """
        Initialize a timeslot directly from a dictionary object.
        """
        return cls(
            ID=json_obj["id"],
            start=json_obj["start"],
            end=json_obj["end"],
            project=json_obj["project"],
            tags=json_obj["tags"],
        )

    def toDict(self) -> dict:
        """
        Returns a dictionary of the timeslot
        """
        obj = {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "project": self.project,
            "tags": self.tags,
        }

        return obj

    def toDictString(self) -> str:
        """
        Returns a JSON-string
        """

        return json.dumps(self.toDict())

    def getDurationHR(self):
        """
        Return the data needed to display Human Readale duration
        """
        hh, remainder = divmod(int(self.duration.total_seconds()), 3600)
        mm, ss = divmod(remainder, 60)

        M = mm
        if ss > 30:
            M = mm + 1

        return {"hh": hh, "H": hh, "mm": mm, "M": M, "ss": ss}

    def toHR(self):
        """
        Returns timeslot in interface friendly format
        """

        tags_hr = " ".join(str(t) for t in self.tags)

        # Make sure time is readable and makes sense
        if self.start_dt.date() == self.end_dt.date():
            start_hr = self.start_dt.strftime("%H:%M")
        else:
            start_hr = self.start_dt.strftime("%H:%M %d-%m-%y")

        end_hr = self.end_dt.strftime("%H:%M %d-%m-%y")

        returnString = f"{self.id} {self.duration} ({start_hr} - {end_hr}) {self.project} {tags_hr}"

        return returnString

    def toCSV(self):
        """
        Creates a CSV line for a timeslot
        """
        return f"{self.id},{self.start},{self.end},{self.project},{self.tags}"

