# Copyright (c) 2023, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document

class GPPinnedProject(Document):
	def before_insert(self):
		self.user = dontmanage.session.user
		self.order = dontmanage.db.count('GP Pinned Project', {'user': self.user}) + 1

		if dontmanage.db.exists('GP Pinned Project', {'user': self.user, 'project': self.project}):
			dontmanage.throw('This project is already pinned')

	@staticmethod
	def get_list_query(query):
		Pin = dontmanage.qb.DocType('GP Pinned Project')
		query = query.where(Pin.user == dontmanage.session.user)
		return query
