# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document
from gameplan.gameplan.doctype.gp_discussion.search import remove_index, update_index
from gameplan.mixins.mentions import HasMentions
from gameplan.mixins.reactions import HasReactions
from gameplan.utils import remove_empty_trailing_paragraphs

class GPComment(HasMentions, HasReactions, Document):
	on_delete_set_null = ["GP Notification"]
	mentions_field = 'content'

	def before_insert(self):
		if self.reference_doctype not in ["GP Discussion"]:
			return

		reference_doc = dontmanage.get_doc(self.reference_doctype, self.reference_name)
		if reference_doc.meta.has_field("closed_at"):
			if reference_doc.closed_at:
				dontmanage.throw("Cannot add comment to a closed discussion")

	def after_insert(self):
		if self.reference_doctype not in ["GP Discussion", "GP Task"]:
			return
		reference_doc = dontmanage.get_doc(self.reference_doctype, self.reference_name)
		if reference_doc.meta.has_field("last_post_at"):
			reference_doc.set("last_post_at", dontmanage.utils.now())
		if reference_doc.meta.has_field("last_post_by"):
			reference_doc.set("last_post_by", dontmanage.session.user)
		if reference_doc.meta.has_field("comments_count"):
			reference_doc.set("comments_count", reference_doc.comments_count + 1)
		if reference_doc.doctype == 'GP Discussion':
			reference_doc.update_participants_count()
		reference_doc.save(ignore_permissions=True)

	def on_trash(self):
		if self.reference_doctype not in ["GP Discussion", "GP Task"]:
			return
		reference_doc = dontmanage.get_doc(self.reference_doctype, self.reference_name)
		if reference_doc.meta.has_field("comments_count"):
			reference_doc.db_set("comments_count", reference_doc.comments_count - 1)

	def validate(self):
		self.content = remove_empty_trailing_paragraphs(self.content)
		self.de_duplicate_reactions()

	def on_update(self):
		self.update_discussion_index()
		self.notify_mentions()
		self.notify_reactions()

	def update_discussion_index(self):
		if self.reference_doctype == "GP Discussion":
			if self.deleted_at:
				remove_index(self)
			else:
				update_index(self)
