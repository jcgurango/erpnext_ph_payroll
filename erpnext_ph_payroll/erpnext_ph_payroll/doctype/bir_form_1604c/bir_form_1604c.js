// Copyright (c) 2023, JC Gurango and contributors
// For license information, please see license.txt

frappe.ui.form.on('BIR Form 1604C', {
	refresh: function(frm) {
		if (!cur_frm.doc.__islocal) {
			frm.page.add_menu_item('Preview', () => {
				window.open('/api/method/erpnext_ph_payroll.erpnext_ph_payroll.preview_form?doctype=' + encodeURIComponent('BIR Form 1604C') + '&docname=' + encodeURIComponent(frm.doc.name));
			});
		}
	},
});

const recompute = function(frm, cdt, cdn) {
	frm.refresh_field('summary_of_remittances');
	locals[cdt][cdn].total_amount_remitted = (locals[cdt][cdn].taxes_withheld || 0) + (locals[cdt][cdn].adjustment || 0) + (locals[cdt][cdn].penalties || 0);
};

frappe.ui.form.on('BIR Form 1604C Month', {
	taxes_withheld: recompute,
	adjustment: recompute,
	penalties: recompute,
});
