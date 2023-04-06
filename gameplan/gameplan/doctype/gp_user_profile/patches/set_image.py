# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def execute():
	UserProfile = dontmanage.qb.DocType('GP User Profile')
	User = dontmanage.qb.DocType('User')
	query = (
		dontmanage.qb.update(UserProfile)
			.set(UserProfile.image, User.user_image)
			.left_join(User).on(UserProfile.user == User.name)
			.where(User.user_image.isnotnull())
	)
	query.run()
