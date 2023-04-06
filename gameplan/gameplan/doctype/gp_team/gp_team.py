# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
import gameplan
from dontmanage.model.document import Document
from dontmanage.model.naming import append_number_if_name_exists
from gameplan.gemoji import get_random_gemoji
from gameplan.mixins.archivable import Archivable
from pypika.terms import ExistsCriterion

class GPTeam(Archivable, Document):
	on_delete_cascade = ["GP Project"]
	on_delete_set_null = ["GP Notification"]

	def as_dict(self, *args, **kwargs) -> dict:
		members = [m.user for m in self.members]
		if self.is_private and dontmanage.session.user not in members:
			dontmanage.throw("Not permitted", dontmanage.PermissionError)

		d = super().as_dict(*args, **kwargs)
		return d

	@staticmethod
	def get_list_query(query):
		Team = dontmanage.qb.DocType('GP Team')
		Member = dontmanage.qb.DocType('GP Member')
		member_exists = (
			dontmanage.qb.from_(Member)
				.select(Member.name)
				.where(Member.parenttype == 'GP Team')
				.where(Member.parent == Team.name)
				.where(Member.user == dontmanage.session.user)
		)
		query = query.where(
			(Team.is_private == 0) | ((Team.is_private == 1) & ExistsCriterion(member_exists))
		)
		is_guest = gameplan.is_guest()
		if is_guest:
			Team = dontmanage.qb.DocType('GP Team')
			GuestAccess = dontmanage.qb.DocType('GP Guest Access')
			team_list = GuestAccess.select(GuestAccess.team).where(GuestAccess.user == dontmanage.session.user)
			query = query.where(Team.name.isin(team_list))
		return query

	def before_insert(self):
		if not self.name:
			slug = dontmanage.scrub(self.title).replace("_", "-")
			self.name = append_number_if_name_exists("GP Team", slug)

		if not self.icon:
			self.icon = get_random_gemoji().emoji

		if not self.readme:
			self.readme = f"""
			<h3>Welcome to the {self.title} team page!</h3>
			<p>You can add a brief introduction about the team, important links, resources, and other important information here.</p>
		"""

		self.add_member(dontmanage.session.user)

	def add_member(self, email):
		if email not in [member.user for member in self.members]:
			self.append("members", {
				"email": email,
				"user": email,
				"status": "Accepted"
			})

	@dontmanage.whitelist()
	def add_members(self, users):
		for user in users:
			self.add_member(user)
		self.save()

	@dontmanage.whitelist()
	def remove_member(self, user):
		for member in self.members:
			if member.user == user:
				self.remove(member)
				self.save()
				break
