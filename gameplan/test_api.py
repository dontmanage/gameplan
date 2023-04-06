# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage

def whitelist(fn):
	if not dontmanage.conf.enable_ui_tests:
		dontmanage.throw("Cannot run UI tests. Set 'enable_ui_tests' in site_config.json to continue.")

	whitelisted = dontmanage.whitelist()(fn)
	return whitelisted


@whitelist
def clear_data(onboard=None):
	doctypes = dontmanage.get_all("DocType", filters={"module": "Gameplan"}, pluck="name")
	for doctype in doctypes:
		dontmanage.db.delete(doctype)

	admin = dontmanage.get_doc('User', 'Administrator')
	admin.add_roles('Gameplan Admin')

	if not dontmanage.db.exists('User', 'john@example.com'):
		dontmanage.get_doc(
			doctype='User',
			email='john@example.com',
			first_name='John',
			last_name='Doe',
			send_welcome_email=0,
			roles=[{'role': 'Gameplan Member'}]
		).insert()

	if not dontmanage.db.exists('User', 'system@example.com'):
		dontmanage.get_doc(
			doctype='User',
			email='system@example.com',
			first_name='System',
			last_name='User',
			send_welcome_email=0,
			roles=[{'role': 'Gameplan Admin'},{'role': 'System Manager'}]
		).insert()

	keep_users = ['Administrator', 'Guest', 'john@example.com', 'system@example.com']
	for user in dontmanage.get_all("User", filters={"name": ["not in", keep_users]}):
		dontmanage.delete_doc("User", user.name)

	if onboard:
		dontmanage.get_doc(doctype='GP Team', title='Test Team').insert()