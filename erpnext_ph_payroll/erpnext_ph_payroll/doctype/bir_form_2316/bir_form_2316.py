# Copyright (c) 2023, JC Gurango and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe.model.document import Document

class BIRForm2316(Document):
	def format_data(self, data, formatted_data):
		formatted_data.year = utils.get_datetime(data.period_from).year
		formatted_data.period_from = utils.get_datetime(data.period_from).strftime('%m%d')
		formatted_data.period_to = utils.get_datetime(data.period_to).strftime('%m%d')

		if data.get('employee_dob'):
			formatted_data.employee_dob = utils.get_datetime(data.employee_dob).strftime('%m%d%Y')

		if formatted_data.employer_type == 'Main':
			formatted_data.is_main_employer = '✓'
		else:
			formatted_data.is_secondary_employer = '✓'

		if data.minimum_wage_earner:
			formatted_data.is_mwe = '✓'

		if formatted_data.get('employee_contact_number'):
			formatted_data['employee_contact_number'] = formatted_data['employee_contact_number'].replace(' ', '')
			if formatted_data.employee_contact_number[0] == '+':
				formatted_data['employee_contact_number'] = formatted_data['employee_contact_number'][1:]
			if formatted_data.employee_contact_number[0:2] == '63':
				formatted_data['employee_contact_number'] = '0' + formatted_data['employee_contact_number'][2:]

		formatted_data['total_non_taxable_compensation'] = formatted_data.get('non_taxable_compensation')
		formatted_data['total_taxable_compensation'] = formatted_data.get('taxable_compensation')

		return formatted_data

	@frappe.whitelist()
	def retrieve_data(self):
		if not self.employee or not self.period_from or not self.period_to:
			return

		employee = frappe.get_doc('Employee', self.employee)

		for document in employee.identification_documents:
			if document.type == 'TIN':
				self.employee_tin = document.identification_number

		self.employee_zip = employee.zip
		self.employee_local_zip = employee.zip

		address = ', '.join(filter(lambda x: x, [employee.street, employee.suburb, employee.city, employee.province, employee.country]))
		self.employee_address = address
		self.employee_local_address = address
		self.employee_contact_number = employee.cell_number

		amounts_raw = frappe.db.sql('''
			SELECT
				detail.abbr,
				SUM(detail.amount) AS `amount`
			FROM `tabSalary Detail` detail
			INNER JOIN `tabSalary Slip` slip ON detail.parent = slip.name
			WHERE
				slip.docstatus = 1
				AND slip.start_date <= %(period_to)s
				AND slip.end_date >= %(period_from)s
				AND slip.employee = %(employee)s
			GROUP BY detail.abbr
			UNION
			SELECT
				'BASIC_PAY',
				SUM(detail.amount) AS `amount`
			FROM `tabSalary Detail` detail
			INNER JOIN `tabSalary Slip` slip ON detail.parent = slip.name
			WHERE
				slip.docstatus = 1
				AND slip.start_date <= %(period_to)s
				AND slip.end_date >= %(period_from)s
				AND slip.employee = %(employee)s
				AND detail.is_basic_pay = 1
		''', values={ 'employee': self.employee, 'period_from': self.period_from, 'period_to': self.period_to }, as_dict=True)
		amounts = { }

		for a in amounts_raw:
			amounts[a['abbr']] = a['amount']
		
		self.other_benefits_mwe = amounts.get('PH_13M', 0)
		self.de_minimis_benefits = amounts.get('NONTAXDEMINIMIS', 0)
		self.contributions = float(amounts.get('PH_SSS', 0)) + float(amounts.get('PH_PHIC', 0)) + float(amounts.get('PH_HDMF', 0))
		self.basic_pay = amounts.get('BASIC_PAY', 0)
		self.overtime_pay = amounts.get('PH_REG_OT', 0)
		self.recompute_totals()

	@frappe.whitelist()
	def recompute_totals(self):
		self.non_taxable_compensation = float(self.get('basic_salary', default=0)) + float(self.get('holiday_pay_mwe', default=0)) + float(self.get('overtime_pay_mwe', default=0)) + float(self.get('night_differential_mwe', default=0)) + float(self.get('hazard_pay_mwe', default=0)) + float(self.get('other_benefits_mwe', default=0)) + float(self.get('de_minimis_benefits', default=0)) + float(self.get('contributions', default=0)) + float(self.get('other_compensation_mwe', default=0)) + float(self.get('total_non_taxable_compensation', default=0))
		self.taxable_compensation = float(self.get('basic_pay', default=0)) + float(self.get('overtime_pay', default=0))
		self.gross_compensation = float(self.get('non_taxable_compensation', default=0)) + float(self.get('taxable_compensation', default=0))
		self.gross_taxable_compensation = float(self.get('taxable_compensation', default=0) or 0) + float(self.get('previous_employer_taxable_compensation', default=0) or 0)
		self.tax_withheld = float(self.get('present_employer_tax_withheld', default=0) or 0) + float(self.get('previous_employer_tax_withheld', default=0) or 0)
		self.total_tax_withheld = float(self.get('pera_tax_credit', default=0) or 0) + float(self.get('tax_withheld', default=0) or 0)

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

	def get_form_fill_template(self):
		return 'PH Payroll - BIR-2316'

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
