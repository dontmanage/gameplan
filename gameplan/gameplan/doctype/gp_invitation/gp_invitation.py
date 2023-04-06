# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document

class GPInvitation(Document):
	def before_insert(self):
		dontmanage.utils.validate_email_address(self.email, True)
		if self.role == 'Gameplan Guest' and not (self.teams or self.projects):
			dontmanage.throw('Team or Project is required to invite as Guest')

		if self.role != 'Gameplan Guest':
			self.teams = None
			self.projects = None

		self.key = dontmanage.generate_hash(length=12)
		self.invited_by = dontmanage.session.user
		self.status = 'Pending'

	def after_insert(self):
		self.invite_via_email()

	def invite_via_email(self):
		invite_link = dontmanage.utils.get_url(
			f"/api/method/gameplan.api.accept_invitation?key={self.key}"
		)
		if dontmanage.local.dev_server:
			print(f"Invite link for {self.email}: {invite_link}")

		title = f'Gameplan'
		template = 'gameplan_invitation'

		dontmanage.sendmail(
			recipients=self.email,
			subject=f"You have been invited to join {title}",
			template=template,
			args={"title": title, "invite_link": invite_link},
			now=True,
		)
		self.db_set('email_sent_at', dontmanage.utils.now())

	def accept(self):
		if self.status == 'Expired':
			dontmanage.throw('Invalid or expired key')

		user = self.create_user_if_not_exists()
		user.append_roles(self.role)
		user.save(ignore_permissions=True)
		self.create_guest_access(user)

		self.status = 'Accepted'
		self.accepted_at = dontmanage.utils.now()
		self.save(ignore_permissions=True)

	def create_guest_access(self, user):
		if self.role == 'Gameplan Guest':
			teams = dontmanage.parse_json(self.teams) if self.teams else []
			for team in teams:
				guest_access = dontmanage.get_doc(doctype='GP Guest Access')
				guest_access.user = user.name
				guest_access.team = team
				guest_access.save(ignore_permissions=True)

			projects = dontmanage.parse_json(self.projects) if self.projects else []
			for project in projects:
				guest_access = dontmanage.get_doc(doctype='GP Guest Access')
				guest_access.user = user.name
				guest_access.project = project
				guest_access.save(ignore_permissions=True)

	def create_user_if_not_exists(self):
		if not dontmanage.db.exists("User", self.email):
			first_name = self.email.split("@")[0].title()
			user = dontmanage.get_doc(
				doctype="User",
				user_type="Website User",
				email=self.email,
				send_welcome_email=0,
				first_name=first_name,
			).insert(ignore_permissions=True)
		else:
			user = dontmanage.get_doc("User", self.email)
		return user

def expire_invitations():
	''' expire invitations after 3 days '''
	from dontmanage.utils import add_days, now

	days = 3
	invitations_to_expire = dontmanage.db.get_all('GP Invitation',
		filters={'status': 'Pending', 'creation': ['<', add_days(now(), -days)]}
	)
	for invitation in invitations_to_expire:
		invitation = dontmanage.get_doc('GP Invitation', invitation.name)
		invitation.status = 'Expired'
		invitation.save(ignore_permissions=True)
