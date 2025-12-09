from django.conf import settings


def secretfile_filter(obj: dict):
	# field = ('id', 'title', 'posted_by', 'expire_at', 'password')
	
	# shaden password
	obj['password'] = bool( obj.get('password') )

	# format timestr
	obj['expire_at'] = obj['expire_at'].strftime(settings.DATETIME_FORMAT)

	return obj