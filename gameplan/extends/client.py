# Copyright (c) 2022, DontManage and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import dontmanage
from dontmanage.model.base_document import get_controller


@dontmanage.whitelist()
def get_list(doctype=None, fields=None, filters=None, order_by=None, start=0, limit=20, group_by=None, parent=None, debug=False):
	check_permissions(doctype, parent)
	query = dontmanage.qb.get_query(
		table=doctype,
		fields=fields,
		filters=filters,
		order_by=order_by,
		offset=start,
		limit=limit,
		group_by=group_by,
	)
	query = apply_custom_filters(doctype, query)
	return query.run(as_dict=True, debug=debug)

def check_permissions(doctype, parent):
	user = dontmanage.session.user
	if (
		not dontmanage.has_permission(doctype, "select", user=user, parent_doctype=parent)
		and not dontmanage.has_permission(doctype, "read", user=user, parent_doctype=parent)
	):
		dontmanage.throw(f'Insufficient Permission for {doctype}', dontmanage.PermissionError)

def apply_custom_filters(doctype, query):
	"""Apply custom filters to query"""
	controller = get_controller(doctype)
	if hasattr(controller, "get_list_query"):
		return_value = controller.get_list_query(query)
		if return_value is not None:
			query = return_value

	return query

@dontmanage.whitelist()
def batch(requests):
	from dontmanage.handler import handle
	from dontmanage.app import handle_exception
	requests = dontmanage.parse_json(requests)
	responses = []

	for i, request_params in enumerate(requests):
		savepoint = f'batch_request_{i}'
		try:
			dontmanage.db.savepoint(savepoint)
			dontmanage.form_dict.update(request_params)
			response = handle()
			dontmanage.db.release_savepoint(savepoint)
		except Exception as e:
			dontmanage.db.rollback(save_point=savepoint)
			response = handle_exception(e)

		responses.append(response)

	return [r.json for r in responses]
