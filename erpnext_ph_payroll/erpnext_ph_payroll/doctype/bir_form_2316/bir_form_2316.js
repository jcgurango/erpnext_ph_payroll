// Copyright (c) 2023, JC Gurango and contributors
// For license information, please see license.txt

const dependent_fields = [
	'previous_employer_taxable_compensation',
	'tax_due',
	'present_employer_tax_withheld',
	'previous_employer_tax_withheld',
	'pera_tax_credit',
	'basic_salary',
	'holiday_pay_mwe',
	'overtime_pay_mwe',
	'night_differential_mwe',
	'hazard_pay_mwe',
	'other_benefits_mwe',
	'de_minimis_benefits',
	'contributions',
	'other_compensation_mwe',
	'basic_pay',
	'overtime_pay',
];

frappe.ui.form.on('BIR Form 2316', {
	refresh: function(frm) {
		if (!cur_frm.doc.__islocal) {
			frm.page.add_menu_item('Preview', () => {
				window.open('/api/method/erpnext_ph_payroll.erpnext_ph_payroll.preview_form?doctype=' + encodeURIComponent('BIR Form 2316') + '&docname=' + encodeURIComponent(frm.doc.name));
			});
		}
	},
	retrieve_data: function(frm) {
		return frappe.call({
			method: 'recompute_totals',
			doc: frm.doc,
			callback: function(r) {
				frm.refresh();
			}
		});
	},
	...dependent_fields.reduce((current, next) => ({
		...current,
		[next]: function(frm) {
			frm.events.retrieve_data(frm);
		},
	}), { }),
});
