

class DetailStatus:
	UndefinedError = -1

	Init = 0
	Success = "File download has started"
	FailNoPassword = "Please provide any password"
	FailPassword = "Password Mismatch"
	FailNoFile = "No File Correspond"
	FailWrongMethod = "Only Post method is alloyed to visit this site"
	FailNoPermission = "You have no permission to access this file"
	FailUnsafeFilename = "Given filename is considered an important system file"

	_ALL_STATUS = (
		Init,
		Success,
		FailNoPassword,
		FailPassword,
		FailNoFile,
		FailWrongMethod,
		FailNoPermission,
		FailUnsafeFilename,
	)

	@classmethod
	def parse(cls, status:str):
		if status and status in cls._ALL_STATUS:
			return status
		return cls.Init
