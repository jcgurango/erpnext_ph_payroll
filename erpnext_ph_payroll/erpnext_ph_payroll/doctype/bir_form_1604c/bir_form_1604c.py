# Copyright (c) 2023, JC Gurango and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from erpnext_ph_payroll.erpnext_ph_payroll.doctype.bir_form import BIRForm

months = {
	'': '',
	'January': '01',
	'February': '02',
	'March': '03',
	'April': '04',
	'May': '05',
	'June': '06',
	'July': '07',
	'August': '08',
	'September': '09',
	'October': '10',
	'November': '11',
	'December': '12'
}

class BIRForm1604C(BIRForm):
	def format_data(self, data, formatted_data):
		data['total_taxes_withheld'] = 0
		data['total_adjustment'] = 0
		data['total_penalties'] = 0
		data['total_total_amount_remitted'] = 0
		formatted_data['amended_return'] = 'X' if data.get('amended_return') else ' X'
		formatted_data['category_of_withholding_agent'] = 'X' if data.get('category_of_withholding_agent') == 'Private' else ' X'
		formatted_data['top_withholding_agent'] = ('X' if data.get('top_withholding_agent') else ' X') if data.get('category_of_withholding_agent') == 'Private' else ''
		formatted_data['refund_date'] = utils.get_datetime(data.refund_date).strftime('%m%d%Y') if data.get('refund_date') else ''
		formatted_data['withholding_agent_name'] = formatted_data.get('withholding_agent_name', '').upper()
		formatted_data['registered_address'] = formatted_data.get('registered_address', '').upper()
		formatted_data['email_address'] = formatted_data.get('email_address', '').upper()
		formatted_data['month_of_first_crediting_of_overremittance'] = months[formatted_data.get('month_of_first_crediting_of_overremittance', '')]
		formatted_data['refund_released'] = 'X' if data.get('refund_released') else ' X'
		formatted_data['overremittance_amount'] = formatted_data['overremittance_amount'] if data.get('refund_released') else ''

		# Flatten list
		child_doctype = frappe.get_meta('BIR Form 1604C Month')

		for i, row in enumerate(data.get('summary_of_remittances') or self.get('summary_of_remittances')):
			for field in child_doctype.fields:
				formatted_data['row_' + str(i) + '_' + field.fieldname] = frappe.format(row.get(field.fieldname), field)

				if field.fieldname in ['taxes_withheld', 'adjustment', 'penalties', 'total_amount_remitted']:
					data['total_' + field.fieldname] += float(row.get(field.fieldname) or 0)

		for field in child_doctype.fields:
			if field.fieldname in ['taxes_withheld', 'adjustment', 'penalties', 'total_amount_remitted']:
				formatted_data['total_' + field.fieldname] = frappe.format(data['total_' + field.fieldname], field)

		return formatted_data

	def get_form_fill_template(self):
		return 'PH Payroll - BIR-1604-C'

	def before_insert(self):
		for month in months.keys():
			if month:
				self.append('summary_of_remittances', {
					'month': month,
				})

	def validate(self):
		for remittance in self.get('summary_of_remittances'):
			remittance.total_amount_remitted = (remittance.get('taxes_withheld') or 0) + (remittance.get('adjustment') or 0) + (remittance.get('penalties') or 0)
