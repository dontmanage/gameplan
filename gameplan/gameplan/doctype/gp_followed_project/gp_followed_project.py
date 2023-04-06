# Copyright (c) 2023, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document

class GPFollowedProject(Document):
	def before_insert(self):
		if not self.user:
			self.user = dontmanage.session.user

	@staticmethod
	def get_list_query(query):
		FollowedProject = dontmanage.qb.DocType('GP Followed Project')
		query = query.where(FollowedProject.user == dontmanage.session.user)
		return query
