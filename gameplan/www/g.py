# Copyright (c) 2022, DontManage and Contributors
# See license.txt

from __future__ import unicode_literals
import dontmanage

no_cache = 1


def get_context(context):
	csrf_token = dontmanage.sessions.get_csrf_token()
	dontmanage.db.commit()
	context.csrf_token = csrf_token
	context.default_route = get_default_route()

def on_login(login_manager):
	dontmanage.response['default_route'] = get_default_route()

def get_default_route():
	if not dontmanage.db.get_all('GP Team', limit=1):
		return '/onboarding'
	else:
		return '/home'
