# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage
from dontmanage.utils import update_progress_bar


def execute():
	discussions = dontmanage.get_all("GP Discussion", pluck="name")
	failed = []
	for i, discussion in enumerate(discussions):
		update_progress_bar("Updating participants count", i, len(discussions), absolute=True)
		doc = dontmanage.get_doc("GP Discussion", discussion)
		try:
			doc.update_participants_count()
			doc.db_set("participants_count", doc.participants_count, update_modified=False)
		except:
			failed.append(discussion)

	if failed:
		print("Failed to update participants count for", failed)
