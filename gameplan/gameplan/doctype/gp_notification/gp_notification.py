# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
import gameplan
from dontmanage.model.document import Document

class GPNotification(Document):
	def after_insert(self):
		gameplan.refetch_resource('Unread Notifications Count', user=self.to_user)

	@staticmethod
	def clear_notifications(discussion=None, comment=None, task=None, user=None):
		if not user:
			user = dontmanage.session.user
		filters = {'to_user': user}
		if discussion:
			filters['discussion'] = discussion
		if comment:
			filters['comment'] = comment
		if task:
			filters['task'] = task

		for notification in dontmanage.get_all('GP Notification', filters=filters):
			doc = dontmanage.get_doc('GP Notification', notification.name)
			doc.read = 1
			doc.save()

		gameplan.refetch_resource('Unread Notifications Count', user=user)
