# Copyright (c) 2023, JC Gurango and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BIRForm(Document):
	def before_insert(self):
		self.retrieve_data()

	def get_form_fill_data(self):
		data = self.get_valid_dict()
		formatted_data = self.get_valid_dict()

		for field in self.meta.fields:
			if data.get(field.fieldname) != None:
				formatted_data[field.fieldname] = frappe.format(data.get(field.fieldname), field)

		data = self.format_data(data, formatted_data)
		remove_list = []

		for key in formatted_data:
			if data.get(key) == None or data.get(key) == '':
				remove_list.append(key)
		
		for key in remove_list:
			formatted_data.pop(key)

		return formatted_data

	def create_form_fill_pdf(self):
		form_fill_template = frappe.get_doc('Form Fill Template', self.get_form_fill_template())
		form_fill_data = form_fill_template.fill_document(self.get_form_fill_data())
		return form_fill_data

	def on_submit(self):
		form_fill_data = self.create_form_fill_pdf()
		file = frappe.get_doc({
			'doctype': 'File',
			'file_name': self.name + '.pdf',
			'attached_to_name': self.name,
			'attached_to_doctype': self.doctype,
			"folder": 'Home/Attachments',
			'content': form_fill_data})
		file.save()
		frappe.msgprint('The generated form has been attached in PDF format.', 'PDF Generated')
