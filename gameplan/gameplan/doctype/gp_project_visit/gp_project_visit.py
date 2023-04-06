# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document

class GPProjectVisit(Document):
	@staticmethod
	def get_list_query(query):
		ProjectVisit = dontmanage.qb.DocType("GP Project Visit")
		query = query.where(ProjectVisit.user == dontmanage.session.user)
		return query
