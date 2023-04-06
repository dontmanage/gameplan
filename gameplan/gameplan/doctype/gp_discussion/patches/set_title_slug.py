# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage


def execute():
    for d in dontmanage.db.get_all('GP Discussion', pluck='name'):
        doc = dontmanage.get_doc('GP Discussion', d)
        doc.update_slug()
        doc.db_set('slug', doc.slug)
