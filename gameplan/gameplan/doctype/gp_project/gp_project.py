# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage, requests, gameplan
from dontmanage.model.document import Document
from gameplan.gemoji import get_random_gemoji
from gameplan.mixins.archivable import Archivable
from gameplan.mixins.manage_members import ManageMembersMixin
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pypika.terms import ExistsCriterion
from gameplan.api import invite_by_email


class GPProject(ManageMembersMixin, Archivable, Document):
	on_delete_cascade = ["GP Task", "GP Discussion"]
	on_delete_set_null = ["GP Notification"]

	@staticmethod
	def get_list_query(query):
		Project = dontmanage.qb.DocType('GP Project')
		Member = dontmanage.qb.DocType('GP Member')
		member_exists = (
			dontmanage.qb.from_(Member)
				.select(Member.name)
				.where(Member.parenttype == 'GP Team')
				.where(Member.parent == Project.team)
				.where(Member.user == dontmanage.session.user)
		)
		query = query.where(
			(Project.is_private == 0) | ((Project.is_private == 1) & ExistsCriterion(member_exists))
		)
		if gameplan.is_guest():
			GuestAccess = dontmanage.qb.DocType('GP Guest Access')
			project_list = GuestAccess.select(GuestAccess.project).where(GuestAccess.user == dontmanage.session.user)
			query = query.where(Project.name.isin(project_list))
		return query

	def as_dict(self, *args, **kwargs) -> dict:
		d = super().as_dict(*args, **kwargs)
		# summary
		total_tasks = dontmanage.db.count("GP Task", {"project": self.name})
		completed_tasks = dontmanage.db.count(
			"GP Task", {"project": self.name, "is_completed": 1}
		)
		pending_tasks = total_tasks - completed_tasks
		overdue_tasks = dontmanage.db.count(
			"GP Task",
			{"project": self.name, "is_completed": 0, "due_date": ("<", dontmanage.utils.today())},
		)
		d.summary = {
			"total_tasks": total_tasks,
			"completed_tasks": completed_tasks,
			"pending_tasks": pending_tasks,
			"overdue_tasks": overdue_tasks,
		}
		d.is_pinned = bool(dontmanage.db.exists("GP Pinned Project", {"project": self.name, "user": dontmanage.session.user}))
		d.is_followed = self.is_followed()
		return d

	def before_insert(self):
		if not self.icon:
			self.icon = get_random_gemoji().emoji

		if not self.readme:
			self.readme = f"""
			<h3>Welcome to the {self.title} page!</h3>
			<p>You can add a brief introduction about this project, links, resources, and other important information here.</p>
			<p></p>
			<p></p>
		"""

		self.append(
			"members",
			{
				"user": dontmanage.session.user,
				"email": dontmanage.session.user,
				"role": "Project Owner",
				"status": "Accepted",
			},
		)

	def before_save(self):
		if dontmanage.db.get_value('GP Team', self.team, 'is_private'):
			self.is_private = True

	def update_progress(self):
		result = dontmanage.db.get_all(
			"GP Task",
			filters={"project": self.name},
			fields=["sum(is_completed) as completed", "count(name) as total"],
		)[0]
		if result.total > 0:
			self.progress = (result.completed or 0) * 100 / result.total
			self.save()
			self.reload()

	def delete_group(self, group):
		tasks = dontmanage.db.count("GP Task", {"project": self.name, "status": group})
		if tasks > 0:
			dontmanage.throw(f"Group {group} cannot be deleted because it has {tasks} tasks")

		for state in self.task_states:
			if state.status == group:
				self.remove(state)
				self.save()
				break

	def get_activities(self):
		activities = []
		activities.append(
			{
				"type": "info",
				"title": "Project created",
				"date": self.creation,
				"user": self.owner,
			}
		)
		status_updates = dontmanage.db.get_all(
			"Team Project Status Update",
			{"project": self.name},
			["creation", "owner", "content", "status"],
			order_by="creation desc",
		)
		for status_update in status_updates:
			activities.append(
				{
					"type": "content",
					"title": "Status Update",
					"content": status_update.content,
					"status": status_update.status,
					"date": dontmanage.utils.get_datetime(status_update.creation),
					"user": status_update.owner,
				}
			)
		activities.sort(key=lambda x: x["date"], reverse=True)
		return activities

	@dontmanage.whitelist()
	def move_to_team(self, team):
		if not team or self.team == team:
			return
		self.team = team
		self.save()
		for doctype in ['GP Task', 'GP Discussion']:
			for name in dontmanage.db.get_all(doctype, {"project": self.name}, pluck="name"):
				doc = dontmanage.get_doc(doctype, name)
				doc.team = self.team
				doc.save()

	@dontmanage.whitelist()
	def invite_guest(self, email):
		invite_by_email(email, role='Gameplan Guest', projects=[self.name])

	@dontmanage.whitelist()
	def remove_guest(self, email):
		name = dontmanage.db.get_value('GP Guest Access', {'project': self.name, 'user': email})
		if name:
			dontmanage.delete_doc('GP Guest Access', name)

	@dontmanage.whitelist()
	def track_visit(self):
		if dontmanage.flags.read_only:
			return

		values = {"user": dontmanage.session.user, "project": self.name}
		existing = dontmanage.db.get_value("GP Project Visit", values)
		if existing:
			visit = dontmanage.get_doc("GP Project Visit", existing)
			visit.last_visit = dontmanage.utils.now()
			visit.save(ignore_permissions=True)
		else:
			visit = dontmanage.get_doc(doctype="GP Project Visit")
			visit.update(values)
			visit.last_visit = dontmanage.utils.now()
			visit.insert(ignore_permissions=True)

	def is_followed(self):
		return bool(dontmanage.db.exists("GP Followed Project", {"project": self.name, "user": dontmanage.session.user}))

	@dontmanage.whitelist()
	def follow(self):
		if not self.is_followed():
			dontmanage.get_doc(doctype="GP Followed Project", project=self.name).insert(ignore_permissions=True)

	@dontmanage.whitelist()
	def unfollow(self):
		follow_id = dontmanage.db.get_value("GP Followed Project", {"project": self.name, "user": dontmanage.session.user})
		dontmanage.delete_doc("GP Followed Project", follow_id)
		dontmanage.errprint(str(self.is_followed()))

def get_meta_tags(url):
	response = requests.get(url, timeout=2, allow_redirects=True)
	soup = BeautifulSoup(response.text, "html.parser")
	title = soup.find("title").text.strip()

	image = None
	favicon = soup.find("link", rel="icon")
	if favicon:
		image = favicon["href"]

	if image and image.startswith("/"):
		image = urljoin(url, image)

	return {"title": title, "image": image}
