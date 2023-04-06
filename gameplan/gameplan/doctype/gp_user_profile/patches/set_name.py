# Copyright (c) 2021, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def execute():
	for user in dontmanage.get_all("GP User Profile"):
		doc = dontmanage.get_doc("GP User Profile", user.name)
		doc.rename(doc.generate_name())
