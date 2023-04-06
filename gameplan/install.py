# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def after_install():
	download_rembg_model()

def download_rembg_model():
	from rembg import new_session
	new_session()
