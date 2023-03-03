import frappe
from io import BytesIO
import zipfile
import frappe
from frappe import utils

def create_bulk_zip(doctype, docs):
  bytes = BytesIO()

  with zipfile.ZipFile(bytes, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for docname in docs:
      files = frappe.db.get_list('File', filters={
        'attached_to_doctype': doctype,
        'attached_to_name': docname,
        'file_name': docname + '.pdf',
      }, pluck='name')
      
      if len(files) > 0:
        file = frappe.get_doc('File', files[0])
        zipf.write(file.get_full_path(), file.file_name)

  return bytes.getvalue()

@frappe.whitelist()
def download_bulk(doctype, docs):
  frappe.local.response['type'] = 'download'
  frappe.local.response['mimetype'] = 'application/zip'
  frappe.local.response['filename'] = 'bulk_export.zip'
  frappe.local.response['filecontent'] = create_bulk_zip(doctype, docs.split(','))

@frappe.whitelist()
def preview_form(doctype, docname):
  form_template = frappe.get_doc(doctype, docname)
  form_fill_data = form_template.create_form_fill_pdf()
  frappe.response['type'] = 'pdf'
  frappe.response['filename'] = 'preview.pdf'
  frappe.response['filecontent'] = form_fill_data

def salary_data_extensions(salary_slip):
  return {
    'ph_sss': lambda pay: calculate_sss_contribution(pay, salary_slip.end_date, 'employee_contribution'),
    'ph_sss_er': lambda pay: calculate_sss_contribution(pay, salary_slip.end_date, 'employer_contribution'),
    'ph_sss_ec': lambda pay: calculate_sss_contribution(pay, salary_slip.end_date, 'employee_compensation'),
    'ph_wtax': lambda adjustment=0: calculate_withholding_tax(salary_slip.posting_date, salary_slip, adjustment=adjustment),
    'ph_13th_month_pay': lambda: calculate_13th_month_pay(salary_slip)
  }

def calculate_sss_contribution(pay, date, field='employee_contribution'):
	contribution_table = frappe.db.get_list('SSS Contribution',
		filters=[
			['effective_date', '<=', date],
			['docstatus', '=', 1]
		],
		order_by='effective_date desc',
		pluck='name'
	)

	if len(contribution_table):
		contribution_table = frappe.get_doc('SSS Contribution', contribution_table[0])

		for row in contribution_table.contribution_table:
			if pay >= row.from_amount and (pay <= row.to_amount or not row.to_amount or row.to_amount <= 0):
				base = row.get(field)
				mpf = 0

				if row.get('mpf_' + field):
					mpf = row.get('mpf_' + field)

				return base + mpf

	return 0

def calculate_withholding_tax(date, salary_slip, adjustment=0):
	net_pay = salary_slip.gross_pay

	for deduction in (salary_slip.get('deductions') or []):
		if deduction.salary_component in ['PH - HDMF Contribution', 'PH - PHIC Contribution', 'PH - SSS Contribution']:
			net_pay -= deduction.amount

	pay = net_pay
	pay += adjustment

	withholding_table = frappe.db.get_list('PH Withholding Tax Table',
		filters=[
			['effective_date', '<=', date],
			['docstatus', '=', 1],
		],
		order_by='effective_date desc',
		pluck='name'
	)

	if len(withholding_table):
		withholding_table = frappe.get_doc('PH Withholding Tax Table', withholding_table[0])
		total_amount = 0

		for row in withholding_table.slabs:
			if pay >= row.from_amount:
				total_amount += min(pay - row.from_amount, row.to_amount - row.from_amount) * (row.percent_withheld / 100)

		return total_amount

	return 0

def calculate_13th_month_pay(salary_slip):
	effective_year = utils.getdate(salary_slip.posting_date).year

	if utils.getdate(salary_slip.posting_date).month <= 4:
		# Last year
		effective_year -= 1

	gross_pay = frappe.db.sql("""
		SELECT sum(detail.amount) as sum
		FROM `tabSalary Detail` as detail
		INNER JOIN `tabSalary Slip` as salary_slip
		ON detail.parent = salary_slip.name
		WHERE
			salary_slip.employee = %(employee)s
			AND detail.parentfield = 'earnings'
			AND YEAR(salary_slip.posting_date) >= %(effective_year)s
			AND YEAR(salary_slip.posting_date) <= %(effective_year)s
			AND salary_slip.name != %(docname)s
			AND detail.is_13th_month_pay_applicable = 1
			AND salary_slip.docstatus = 1""",
			{'employee': salary_slip.employee, 'effective_year': effective_year, 'docname': salary_slip.name}
	)

	gross_pay = ((gross_pay[0][0] if gross_pay else 0) or 0)

	if utils.getdate(salary_slip.posting_date).year == effective_year:
		for earning in salary_slip.earnings:
			if utils.cint(earning.is_13th_month_pay_applicable):
				gross_pay += earning.amount

	return gross_pay / 12
