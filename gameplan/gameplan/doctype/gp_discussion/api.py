# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage
import gameplan
from pypika.terms import ExistsCriterion


@dontmanage.whitelist()
def get_discussions(filters=None, limit_start=None, limit_page_length=None):
	if not dontmanage.has_permission('GP Discussion', 'read'):
		dontmanage.throw('Insufficient Permission for GP Discussion', dontmanage.PermissionError)

	filters = dontmanage.parse_json(filters) if filters else None
	feed_type = filters.pop('feed_type', None) if filters else None
	Discussion = dontmanage.qb.DocType('GP Discussion')
	Visit = dontmanage.qb.DocType('GP Discussion Visit')
	Project = dontmanage.qb.DocType('GP Project')
	Team = dontmanage.qb.DocType('GP Team')
	Member = dontmanage.qb.DocType('GP Member')
	member_exists = (
		dontmanage.qb.from_(Member)
			.select(Member.name)
			.where(Member.parenttype == 'GP Team')
			.where(Member.parent == Project.team)
			.where(Member.user == dontmanage.session.user)
	)
	query = (
		dontmanage.qb.from_(Discussion)
		.select(
			Discussion.star, Visit.last_visit, Project.title.as_('project_title'), Team.title.as_('team_title')
		)
		.left_join(Visit)
		.on((Discussion.name == Visit.discussion) & (Visit.user == dontmanage.session.user))
		.left_join(Project)
		.on(Discussion.project == Project.name)
		.left_join(Team)
		.on(Discussion.team == Team.name)
		.where(
			(Project.is_private == 0) | ((Project.is_private == 1) & ExistsCriterion(member_exists))
		)
		.limit(limit_page_length)
		.offset(limit_start or 0)
	)
	if filters:
		for key in filters:
			query = query.where(Discussion[key] == filters[key])

		# order by pinned_at desc if project is selected
		if filters.get('project'):
			query = query.orderby(Discussion.pinned_at, order=dontmanage._dict(value="desc"))

	if feed_type == 'unread':
		query = query.where((Visit.last_visit < Discussion.last_post_at) | (Visit.last_visit.isnull()))

	if feed_type == 'following':
		FollowedProject = dontmanage.qb.DocType('GP Followed Project')
		followed_projects = FollowedProject.select(FollowedProject.project).where(FollowedProject.user == dontmanage.session.user)
		query = query.where(Discussion.project.isin(followed_projects))

	# default order by last_post_at desc
	query = query.orderby(Discussion.last_post_at, order=dontmanage._dict(value="desc"))

	is_guest = gameplan.is_guest()
	if is_guest:
		GuestAccess = dontmanage.qb.DocType('GP Guest Access')
		project_list = GuestAccess.select(GuestAccess.project).where(GuestAccess.user == dontmanage.session.user)
		query = query.where(Discussion.project.isin(project_list))

	return query.run(as_dict=1)



def highlight_matched_words(text, keywords, strip_content=False):
	words = remove_falsy_values(text.split(' '))
	matches = []
	for i, word in enumerate(words):
		if word.lower() in keywords:
			matches.append(i)
			words[i] = f'<mark class="bg-yellow-100">{word}</mark>'

	if matches:
		if strip_content:
			min_match = min(matches)
			max_match = min_match + 8
			left = min_match - 2
			right = max_match + 2
			left = left if left >= 0 else 0
			right = right if right < len(words) else len(words) - 1
			words = words[left:right]
	else:
		if strip_content:
			words = []

	return ' '.join(words)


def remove_falsy_values(items):
	return [item for item in items if item]
