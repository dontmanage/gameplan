# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


class Archivable:
	'''
	Mixin to add archive and unarchive methods to a DocType. `archived_at` (Datetime) and
	`archived_by` (Link to User) fields are required for this mixin to work.
	'''
	@dontmanage.whitelist()
	def archive(self):
		self.archived_at = dontmanage.utils.now()
		self.archived_by = dontmanage.session.user
		self.save()

	@dontmanage.whitelist()
	def unarchive(self):
		self.archived_at = None
		self.archived_by = None
		self.save()