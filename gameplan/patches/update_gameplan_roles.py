# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def execute():
	HasRole = dontmanage.qb.DocType('Has Role')
	query = dontmanage.qb.update(HasRole).set(HasRole.role, 'Gameplan Member').where(HasRole.role == 'Teams User')
	query.run()

	dontmanage.delete_doc_if_exists('Role', 'Teams User')
