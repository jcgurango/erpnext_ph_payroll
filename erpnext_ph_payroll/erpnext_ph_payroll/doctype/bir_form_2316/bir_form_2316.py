# Copyright (c) 2023, JC Gurango and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe.model.document import Document

class BIRForm2316(Document):
	def get_form_fill_data(self):
		data = self.get_valid_dict()
		data.year = utils.get_datetime(self.period_from).year
		data.period_from = utils.get_datetime(self.period_from).strftime('%m%d')
		data.period_to = utils.get_datetime(self.period_to).strftime('%m%d')
		return data

	def get_form_fill_template(self):
		return 'PH Payroll - BIR-2316'

	@frappe.whitelist()
	def test(self):
		form_fill_template = frappe.get_doc('Form Fill Template', 'PH Payroll - BIR-2316')
		return form_fill_template.fill_document(self.get_form_fill_data())

	def on_submit(self):
		form_fill_template = frappe.get_doc('Form Fill Template', self.get_form_fill_template())
		form_fill_data = form_fill_template.fill_document(self.get_form_fill_data())
		file = frappe.get_doc({
			'doctype': 'File',
			'file_name': self.name + '.pdf',
			'attached_to_name': self.name,
			'attached_to_doctype': self.doctype,
			"folder": 'Home/Attachments',
			'content': form_fill_data})
		file.save()
		frappe.msgprint('The generated form has been attached in PDF format.', 'PDF Generated')
