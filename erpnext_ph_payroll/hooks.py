import frappe
from frappe import utils
from . import __version__ as app_version

app_name = "erpnext_ph_payroll"
app_title = "ERPNext PH Payroll"
app_publisher = "JC Gurango"
app_description = "Standard functions, reports, and salary components for PH Payroll."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "jc@jcgurango.com"
app_license = "MIT"

fixtures = [
	{"dt": "Report", "filters": [["name", "like", "PH - %"]]},
	{"dt": "Salary Component", "filters": [["disabled", "=", False], ["name", "like", "PH - %"]]},
	{"dt": "Salary Structure", "filters": [["docstatus", "=", "1"], ["name", "like", "PH - %"]]},
	{"dt": "PH Withholding Tax Table"},
]

salary_data_extensions = [
	lambda salary_slip: {
		'ph_sss': lambda pay: calculate_sss_contribution(pay, salary_slip.end_date, 'employee_contribution'),
		'ph_sss_er': lambda pay: calculate_sss_contribution(pay, salary_slip.end_date, 'employer_contribution'),
		'ph_sss_ec': lambda pay: calculate_sss_contribution(pay, salary_slip.end_date, 'employee_compensation'),
		'ph_wtax': lambda: calculate_withholding_tax(salary_slip.posting_date, salary_slip),
		'ph_13th_month_pay': lambda: calculate_13th_month_pay(salary_slip)
	}
]

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

				return base + mpf

	return 0

def calculate_withholding_tax(pay, date, salary_slip, basis='monthly'):
	net_pay = salary_slip.gross_pay

	for deduction in (salary_slip.get('deductions') or []):
		if deduction.salary_component in ['PH - HDMF Contribution', 'PH - PHIC Contribution', 'PH - SSS Contribution']:
			net_pay -= deduction.amount

	pay = net_pay

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

	return ((gross_pay[0][0] if gross_pay else 0) or 0) / 12

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_ph_payroll/css/erpnext_ph_payroll.css"
# app_include_js = "/assets/erpnext_ph_payroll/js/erpnext_ph_payroll.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_ph_payroll/css/erpnext_ph_payroll.css"
# web_include_js = "/assets/erpnext_ph_payroll/js/erpnext_ph_payroll.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_ph_payroll/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpnext_ph_payroll.utils.jinja_methods",
# 	"filters": "erpnext_ph_payroll.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpnext_ph_payroll.install.before_install"
# after_install = "erpnext_ph_payroll.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erpnext_ph_payroll.uninstall.before_uninstall"
# after_uninstall = "erpnext_ph_payroll.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_ph_payroll.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_ph_payroll.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_ph_payroll.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_ph_payroll.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_ph_payroll.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_ph_payroll.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpnext_ph_payroll.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_ph_payroll.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_ph_payroll.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_ph_payroll.auth.validate"
# ]

