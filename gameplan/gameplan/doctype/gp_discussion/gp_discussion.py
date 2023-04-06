# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt
import re
import dontmanage
from dontmanage.model.document import Document
from gameplan.gameplan.doctype.gp_discussion.search import update_index
from gameplan.gameplan.doctype.gp_notification.gp_notification import GPNotification
from gameplan.mixins.activity import HasActivity
from gameplan.mixins.mentions import HasMentions
from gameplan.mixins.reactions import HasReactions
from gameplan.utils import remove_empty_trailing_paragraphs

class GPDiscussion(HasActivity, HasMentions, HasReactions, Document):
	on_delete_cascade = ['GP Comment', 'GP Discussion Visit']
	on_delete_set_null = ['GP Notification']
	activities = ['Discussion Closed', 'Discussion Reopened', 'Discussion Title Changed', 'Discussion Pinned', 'Discussion Unpinned']
	mentions_field = 'content'

	def as_dict(self, *args, **kwargs):
		d = super(GPDiscussion, self).as_dict(*args, **kwargs)
		last_visit = dontmanage.db.get_value('GP Discussion Visit', {'discussion': self.name, 'user': dontmanage.session.user}, 'last_visit')
		result = dontmanage.db.get_all(
			'GP Comment',
			filters={'reference_doctype': self.doctype, 'reference_name': self.name, 'creation': ('>', last_visit)},
			order_by='creation asc',
			limit=1,
			pluck='name'
		)
		d.last_unread_comment = result[0] if result else None
		return d

	def before_insert(self):
		self.last_post_at = dontmanage.utils.now()
		self.update_participants_count()

	def after_insert(self):
		self.update_discussions_count(1)

	def on_trash(self):
		self.update_discussions_count(-1)

	def validate(self):
		self.content = remove_empty_trailing_paragraphs(self.content)
		self.title = self.title.strip()
		self.de_duplicate_reactions()

	def on_update(self):
		self.notify_mentions()
		self.notify_reactions()
		self.log_title_update()
		self.update_participants_count()
		self.update_search_index()

	def before_save(self):
		self.update_slug()

	def update_slug(self):
		# remove special characters from title and set as slug
		if not self.title:
			return
		slug = re.sub(r'[^A-Za-z0-9\s-]+', '', self.title.lower())
		slug = slug.replace('\n', ' ')
		slug = slug.split(' ')
		slug = [part for part in slug if part]
		slug = '-'.join(slug)
		slug = re.sub('[-]+', '-', slug)
		self.slug = slug

	def log_title_update(self):
		if self.has_value_changed('title') and self.get_doc_before_save():
			self.log_activity('Discussion Title Changed', data={
				'old_title': self.get_doc_before_save().title,
				'new_title': self.title
			})

	def update_search_index(self):
		if self.has_value_changed('title') or self.has_value_changed('content'):
			update_index(self)

	def update_participants_count(self):
		participants = dontmanage.db.get_all('GP Comment',
			filters={
				'reference_doctype': self.doctype,
				'reference_name': self.name
			},
			pluck='owner'
		)
		participants.append(self.owner)
		self.participants_count = len(list(set(participants)))

	@dontmanage.whitelist()
	def track_visit(self):
		if dontmanage.flags.read_only:
			return

		values = {"user": dontmanage.session.user, "discussion": self.name}
		existing = dontmanage.db.get_value("GP Discussion Visit", values)
		if existing:
			visit = dontmanage.get_doc("GP Discussion Visit", existing)
			visit.last_visit = dontmanage.utils.now()
			visit.save(ignore_permissions=True)
		else:
			visit = dontmanage.get_doc(doctype="GP Discussion Visit")
			visit.update(values)
			visit.last_visit = dontmanage.utils.now()
			visit.insert(ignore_permissions=True)

		# also mark notifications as read
		GPNotification.clear_notifications(discussion=self.name)


	@dontmanage.whitelist()
	def move_to_project(self, project):
		if not project or project == self.project:
			return

		self.project = project
		self.team = dontmanage.db.get_value("GP Project", project, "team")
		self.save()

	@dontmanage.whitelist()
	def close_discussion(self):
		if self.closed_at:
			return
		self.closed_at = dontmanage.utils.now()
		self.closed_by = dontmanage.session.user
		self.log_activity('Discussion Closed')
		self.save()

	@dontmanage.whitelist()
	def reopen_discussion(self):
		if not self.closed_at:
			return
		self.closed_at = None
		self.closed_by = None
		self.log_activity('Discussion Reopened')
		self.save()

	@dontmanage.whitelist()
	def pin_discussion(self):
		if self.pinned_at:
			return
		self.pinned_at = dontmanage.utils.now()
		self.pinned_by = dontmanage.session.user
		self.log_activity('Discussion Pinned')
		self.save()

	@dontmanage.whitelist()
	def unpin_discussion(self):
		if not self.pinned_at:
			return
		self.pinned_at = None
		self.pinned_by = None
		self.log_activity('Discussion Unpinned')
		self.save()

	def update_discussions_count(self, delta=1):
		project = dontmanage.get_doc("GP Project", self.project)
		project.discussions_count = project.discussions_count + delta
		project.save(ignore_permissions=True)
