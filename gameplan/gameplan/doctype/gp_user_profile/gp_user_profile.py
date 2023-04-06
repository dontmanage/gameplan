# Copyright (c) 2022, DontManage Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import dontmanage
import gameplan
from dontmanage.model.document import Document
from dontmanage.model.naming import append_number_if_name_exists
from dontmanage.website.utils import cleanup_page_name
from gameplan.gameplan.doctype.gp_user_profile.profile_photo import remove_background


class GPUserProfile(Document):
	def autoname(self):
		self.name = self.generate_name()

	def generate_name(self):
		full_name = dontmanage.db.get_value("User", self.user, "full_name")
		return append_number_if_name_exists(self.doctype, cleanup_page_name(full_name))

	@dontmanage.whitelist()
	def set_image(self, image):
		self.image = image
		self.is_image_background_removed = False
		self.image_background_color = None
		self.original_image = None
		self.save()
		gameplan.refetch_resource('Users')

	@dontmanage.whitelist()
	def remove_image_background(self, default_color=None):
		if not self.image:
			dontmanage.throw('Profile image not found')
		file = dontmanage.get_doc('File', {'file_url': self.image })
		self.original_image = file.file_url
		image_content = remove_background(file)
		filename, extn = file.get_extension()
		output_filename = f'{filename}_no_bg.png'
		new_file = dontmanage.get_doc(
			doctype="File",
			file_name=output_filename,
			content=image_content,
			is_private=0,
			attached_to_doctype=self.doctype,
			attached_to_name=self.name
		).insert()
		self.image = new_file.file_url
		self.is_image_background_removed = True
		self.image_background_color = default_color
		self.save()
		gameplan.refetch_resource('Users')

	@dontmanage.whitelist()
	def revert_image_background(self):
		if self.original_image:
			self.image = self.original_image
			self.original_image = None
			self.is_image_background_removed = False
			self.image_background_color = None
			self.save()
			gameplan.refetch_resource('Users')


def create_user_profile(doc, method=None):
	if not dontmanage.db.exists("GP User Profile", {"user": doc.name}):
		dontmanage.get_doc(doctype="GP User Profile", user=doc.name).insert(ignore_permissions=True)
		dontmanage.db.commit()

def delete_user_profile(doc, method=None):
	exists = dontmanage.db.exists("GP User Profile", {"user": doc.name})
	if exists:
		return dontmanage.get_doc("GP User Profile", {"user": doc.name}).delete()

def on_user_update(doc, method=None):
	create_user_profile(doc)
	if any(doc.has_value_changed(field) for field in ["full_name", "enabled"]):
		profile = dontmanage.get_doc("GP User Profile", {"user": doc.name})
		profile.enabled = doc.enabled
		profile.full_name = doc.full_name
		profile.save(ignore_permissions=True)
