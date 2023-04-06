
import dontmanage
__version__ = '0.0.1'

def is_guest():
	if dontmanage.session.user == 'Administrator':
		return False
	return 'Gameplan Guest' in dontmanage.get_roles()

def refetch_resource(cache_key: str | list, user=None):
	dontmanage.publish_realtime(
		'refetch_resource',
		{'cache_key': cache_key},
		user=user or dontmanage.session.user,
		after_commit=True
	)