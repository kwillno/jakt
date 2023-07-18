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

class JaktInputError(JaktError):
	pass