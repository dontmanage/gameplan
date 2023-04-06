# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def execute():
	dontmanage.db.delete("GP Member", {'user': ['is', 'not set']})
