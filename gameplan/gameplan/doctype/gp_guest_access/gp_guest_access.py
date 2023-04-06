# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import dontmanage
from dontmanage.model.document import Document
from gameplan.mixins.on_delete import delete_linked_records

class GPGuestAccess(Document):
	pass

def on_user_delete(doc, method):
	delete_linked_records("User", doc.name, ["GP Guest Access"])
