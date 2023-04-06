# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
import gameplan
from dontmanage.model.document import Document

class GPDiscussionVisit(Document):
	def after_insert(self):
		gameplan.refetch_resource('UnreadItems', user=self.user)

	def on_change(self):
		if self.has_value_changed('last_visit'):
			gameplan.refetch_resource('UnreadItems', user=self.user)
