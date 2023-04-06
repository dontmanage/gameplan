# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage
from dontmanage.model.rename_doc import rename_doc


def execute():
	if dontmanage.db.exists("DocType", "Team Project Status Update") and not dontmanage.db.exists(
		"DocType", "Team Discussion"
	):
		rename_doc("DocType", "Team Project Status Update", "Team Discussion")
