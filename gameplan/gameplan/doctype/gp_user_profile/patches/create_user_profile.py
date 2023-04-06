# Copyright (c) 2021, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def execute():
	for user in dontmanage.get_all("User"):
		if user.name in ["Administrator", "Guest"]:
			continue
		dontmanage.get_doc(doctype="GP User Profile", user=user.name).insert(ignore_if_duplicate=True)
