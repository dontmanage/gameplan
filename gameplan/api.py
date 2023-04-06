# Copyright (c) 2021, DontManage and Contributors
# See license.txt

from __future__ import unicode_literals
import gameplan
import dontmanage
from dontmanage.utils import validate_email_address, split_emails
from gameplan.utils import validate_type


@dontmanage.whitelist(allow_guest=True)
def get_user_info(user=None):
	if dontmanage.session.user == "Guest":
		dontmanage.throw("Authentication failed", exc=dontmanage.AuthenticationError)

	filters = [
		['User', 'enabled', '=', 1],
		["Has Role", "role", "like", "Gameplan %"]
	]
	if user:
		filters.append(["User", "name", "=", user])
	users = dontmanage.db.get_all(
		"User",
		filters=filters,
		fields=["name", "email", "user_image", "full_name", "user_type"],
		order_by="full_name asc",
		distinct=True
	)
	# bug: order_by isn't applied when distinct=True
	users.sort(key=lambda x: x.full_name)
	roles = dontmanage.db.get_all('Has Role',
		filters={'parenttype': 'User'},
		fields=['role', 'parent']
	)
	user_profiles = dontmanage.db.get_all('GP User Profile',
		fields=['user', 'name', 'image', 'image_background_color', 'is_image_background_removed'],
		filters={'user': ['in', [u.name for u in users]]}
	)
	user_profile_map = {u.user: u for u in user_profiles}
	for user in users:
		if dontmanage.session.user == user.name:
			user.session_user = True
		user_profile = user_profile_map.get(user.name)
		if user_profile:
			user.user_profile = user_profile.name
			user.user_image = user_profile.image
			user.image_background_color = user_profile.image_background_color
			user.is_image_background_removed = user_profile.is_image_background_removed
		user_roles = [r.role for r in roles if r.parent == user.name]
		user.role = None
		for role in ['Gameplan Guest', 'Gameplan Member', 'Gameplan Admin']:
			if role in user_roles:
				user.role = role
	return users


@dontmanage.whitelist()
@validate_type
def change_user_role(user: str, role: str):
	if gameplan.is_guest():
		dontmanage.throw('Only Admin can change user roles')

	if role not in ['Gameplan Guest', 'Gameplan Member', 'Gameplan Admin']:
		return get_user_info(user)[0]

	user_doc = dontmanage.get_doc('User', user)
	for _role in user_doc.roles:
		if _role.role in ['Gameplan Guest', 'Gameplan Member', 'Gameplan Admin']:
			user_doc.remove(_role)
	user_doc.append_roles(role)
	user_doc.save(ignore_permissions=True)

	return get_user_info(user)[0]


@dontmanage.whitelist()
@validate_type
def remove_user(user: str):
	user_doc = dontmanage.get_doc('User', user)
	user_doc.enabled = 0
	user_doc.save(ignore_permissions=True)
	return user


@dontmanage.whitelist()
@validate_type
def invite_by_email(emails: str, role: str, projects: list = None):
	if not emails:
		return
	email_string = validate_email_address(emails, throw=False)
	email_list = split_emails(email_string)
	if not email_list:
		return
	existing_members = dontmanage.db.get_all('User', filters={'email': ['in', email_list]}, pluck='email')
	existing_invites = dontmanage.db.get_all('GP Invitation',
		filters={
			'email': ['in', email_list],
			'role': ['in', ['Gameplan Admin', 'Gameplan Member']]
		},
		pluck='email')
	to_invite = list(set(email_list) - set(existing_members) - set(existing_invites))
	if projects:
		projects = dontmanage.as_json(projects, indent=None)

	for email in to_invite:
		dontmanage.get_doc(
			doctype='GP Invitation',
			email=email,
			role=role,
			projects=projects
		).insert(ignore_permissions=True)


@dontmanage.whitelist()
def unread_notifications():
	res = dontmanage.db.get_all('GP Notification', 'count(name) as count', {'to_user': dontmanage.session.user, 'read': 0})
	return res[0].count


@dontmanage.whitelist(allow_guest=True)
@validate_type
def accept_invitation(key: str = None):
	if not key:
		dontmanage.throw("Invalid or expired key")

	result = dontmanage.db.get_all(
		"GP Invitation", filters={"key": key}, pluck='name'
	)
	if not result:
		dontmanage.throw("Invalid or expired key")

	invitation = dontmanage.get_doc('GP Invitation', result[0])
	invitation.accept()
	invitation.reload()

	if invitation.status == "Accepted":
		dontmanage.local.login_manager.login_as(invitation.email)
		dontmanage.local.response["type"] = "redirect"
		dontmanage.local.response["location"] = "/g"


@dontmanage.whitelist()
def get_unsplash_photos(keyword=None):
	from gameplan.unsplash import get_list, get_by_keyword

	if keyword:
		return get_by_keyword(keyword)

	return dontmanage.cache().get_value("unsplash_photos", generator=get_list)


@dontmanage.whitelist()
def get_unread_items():
	from dontmanage.query_builder.functions import Count
	Discussion = dontmanage.qb.DocType("GP Discussion")
	Visit = dontmanage.qb.DocType("GP Discussion Visit")
	query = (
		dontmanage.qb.from_(Discussion)
			.select(Discussion.team, Count(Discussion.team).as_("count"))
			.left_join(Visit)
			.on((Visit.discussion == Discussion.name) & (Visit.user == dontmanage.session.user))
			.where((Visit.last_visit.isnull()) | (Visit.last_visit < Discussion.last_post_at))
			.groupby(Discussion.team)
	)
	is_guest = gameplan.is_guest()
	if is_guest:
		GuestAccess = dontmanage.qb.DocType('GP Guest Access')
		project_list = GuestAccess.select(GuestAccess.project).where(GuestAccess.user == dontmanage.session.user)
		query = query.where(Discussion.project.isin(project_list))

	data = query.run(as_dict=1)
	out = {}
	for d in data:
		out[d.team] = d.count
	return out

@dontmanage.whitelist()
def get_unread_items_by_project(projects):
	from dontmanage.query_builder.functions import Count

	project_names = dontmanage.parse_json(projects)
	Discussion = dontmanage.qb.DocType("GP Discussion")
	Visit = dontmanage.qb.DocType("GP Discussion Visit")
	query = (
		dontmanage.qb.from_(Discussion)
			.select(Discussion.project, Count(Discussion.project).as_("count"))
			.left_join(Visit)
			.on((Visit.discussion == Discussion.name) & (Visit.user == dontmanage.session.user))
			.where((Visit.last_visit.isnull()) | (Visit.last_visit < Discussion.last_post_at))
			.where(Discussion.project.isin(project_names))
			.groupby(Discussion.project)
	)

	data = query.run(as_dict=1)
	out = {}
	for d in data:
		out[d.project] = d.count
	return out


@dontmanage.whitelist()
def mark_all_notifications_as_read():
	for d in dontmanage.db.get_all('GP Notification', filters={'to_user': dontmanage.session.user, 'read': 0}, pluck='name'):
		doc = dontmanage.get_doc('GP Notification', d)
		doc.read = 1
		doc.save(ignore_permissions=True)


@dontmanage.whitelist()
def recent_projects():
	from dontmanage.query_builder.functions import Max

	ProjectVisit = dontmanage.qb.DocType('GP Project Visit')
	Team = dontmanage.qb.DocType('GP Team')
	Project = dontmanage.qb.DocType('GP Project')
	Pin = dontmanage.qb.DocType('GP Pinned Project')
	pinned_projects_query = dontmanage.qb.from_(Pin).select(Pin.project).where(Pin.user == dontmanage.session.user)
	projects = (
		dontmanage.qb.from_(ProjectVisit)
			.select(
				ProjectVisit.project.as_('name'),
				Project.team,
				Project.title.as_('project_title'),
				Team.title.as_('team_title'),
				Project.icon,
				Max(ProjectVisit.last_visit).as_('timestamp')
			)
			.left_join(Project).on(Project.name == ProjectVisit.project)
			.left_join(Team).on(Team.name == Project.team)
			.groupby(ProjectVisit.project)
			.where(ProjectVisit.user == dontmanage.session.user)
			.where(ProjectVisit.project.notin(pinned_projects_query))
			.orderby(ProjectVisit.last_visit, order=dontmanage.qb.desc)
			.limit(12)
	)

	return projects.run(as_dict=1)


@dontmanage.whitelist()
def active_projects():
	from dontmanage.query_builder.functions import Count

	Comment = dontmanage.qb.DocType('GP Comment')
	Discussion = dontmanage.qb.DocType('GP Discussion')
	CommentCount = Count(Comment.name).as_('comments_count')
	active_projects = (
		dontmanage.qb.from_(Comment)
			.select(CommentCount, Discussion.project)
			.left_join(Discussion).on(Discussion.name == Comment.reference_name)
			.where(Comment.reference_doctype == 'GP Discussion')
			.where(Comment.creation > dontmanage.utils.add_days(dontmanage.utils.now(), -70))
			.groupby(Discussion.project)
			.orderby(CommentCount, order=dontmanage.qb.desc)
			.limit(12)
	).run(as_dict=1)

	projects = dontmanage.qb.get_query('GP Project',
		fields=['name', 'title as project_title', 'team', 'team.title as team_title', 'icon', 'modified as timestamp'],
		filters={'name': ('in', [d.project for d in active_projects])}
	).run(as_dict=1)

	active_projects_comment_count = {d.project: d.comments_count for d in active_projects}
	for d in projects:
		d.comments_count = active_projects_comment_count.get(str(d.name), 0)

	projects.sort(key=lambda d: d.comments_count, reverse=True)

	return projects







@dontmanage.whitelist()
def onboarding(data):
	data = dontmanage.parse_json(data)
	team = dontmanage.get_doc(doctype='GP Team', title=data.team).insert()
	dontmanage.get_doc(doctype='GP Project', team=team.name, title=data.project).insert()
	emails = ', '.join(data.emails)
	invite_by_email(emails, role='Gameplan Member')
	return team.name

@dontmanage.whitelist(allow_guest=True)
def oauth_providers():
	from dontmanage.utils.html_utils import get_icon_html
	from dontmanage.utils.password import get_decrypted_password
	from dontmanage.utils.oauth import get_oauth2_authorize_url, get_oauth_keys

	out = []
	providers = dontmanage.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = None
		if provider.icon:
			if provider.provider_name == "Custom":
				icon = get_icon_html(provider.icon, small=True)
			else:
				icon = f"<img src='{provider.icon}' alt={provider.provider_name}>"

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			out.append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, '/g/home'),
					"icon": icon,
				}
			)
	return out
