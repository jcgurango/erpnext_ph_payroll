// Copyright (c) 2023, JC Gurango and contributors
// For license information, please see license.txt

function total_non_taxable_compensation(frm, doc, input_name){
	if(!doc){
		frm.set_value(input_name, 0)
	}
	let total_non_taxable = frm.doc.statutory_minimum + frm.doc.holiday_pay + frm.doc.thirteenth_month_pay + frm.doc.de_minimis + frm.doc.mandatory_contributions + frm.doc.other_non_taxable
	let total_taxable = frm.doc.total_amount_compensation - total_non_taxable
	frm.set_value('total_non_taxable', total_non_taxable)
	frm.set_value('total_taxable_compensation', total_taxable)
}

function net_taxable_compensation(frm, doc, input_name){
	if(!doc){
		frm.set_value(input_name, 0)
	}
	let net_taxable = frm.doc.total_taxable_compensation - doc
	frm.set_value('net_taxable', net_taxable)
}

function taxes_withheld_for_remittance(frm, doc, input_name){
	if(!doc){
		frm.set_value(input_name, 0)
	}

	let taxes_withheld_for_remittance = frm.doc.total_taxes_withheld + frm.doc.add_less_adjustment
	
	frm.set_value('taxes_withheld_for_remittance', taxes_withheld_for_remittance)
}
function total_remittances_made(frm, doc, input_name){
	if(!doc){
		frm.set_value(input_name, 0)
	}

	let total_remittances_made = frm.doc.less_tax_remitted + frm.doc.other_remittances_made
	frm.set_value('total_remittances_made', total_remittances_made)
}

function tax_still_due(frm){
	let tax_still_due = frm.doc.taxes_withheld_for_remittance - frm.doc.total_remittances_made
	frm.set_value('tax_still_due', tax_still_due)
}

function total_penalties(frm, doc, input_name){
	if(!doc){
		frm.set_value(input_name, 0)
	}

	let total_penalties = frm.doc.surcharge + frm.doc.interest + frm.doc.compromise
	frm.set_value('total_penalties', total_penalties)
}

frappe.ui.form.on('BIR Form 1601-C', {
	// refresh: function(frm) {

	// }

	onload: function(frm){
		// if the company is set on new doc, fetch and set.
		if(frm.doc.company){
			frappe.db.get_doc('Company', frm.doc.company)
				.then(doc => {
					console.log(doc)
					frm.set_value('tax_id', doc.tax_id)
					frm.set_value('pres_rdo', doc.pres_rdo)
					frm.set_value('company_name', doc.name)
					frm.set_value('company_address', doc.country)
					frm.set_value('zip', doc.zip)
					frm.set_value('phone_no', doc.phone_no)
					frm.set_value('email', doc.email)
				})
		}
	},

	// Fetch and set on get company
	company: function(frm){
		frappe.db.get_doc('Company', frm.doc.company)
			.then(doc => {
				frm.set_value('tax_id', doc.tax_id)
			})
	},

	// Total non taxable and taxable compensation reactivity
	total_amount_compensation: function(frm){
		total_non_taxable_compensation(frm, frm.doc.total_amount_compensation, 'total_amount_compensation')
	},
	statutory_minimum: function(frm){
		total_non_taxable_compensation(frm, frm.doc.statutory_minimum, 'statutory_minimum')
	},
	holiday_pay: function(frm){
		total_non_taxable_compensation(frm, frm.doc.holiday_pay, 'holiday_pay')
	},
	thirteenth_month_pay: function(frm){
		total_non_taxable_compensation(frm, frm.doc.thirteenth_month_pay, 'thirteenth_month_pay')
	},
	de_minimis: function(frm){
		total_non_taxable_compensation(frm, frm.doc.de_minimis, 'de_minimis')
	},
	mandatory_contributions: function(frm){
		total_non_taxable_compensation(frm, frm.doc.mandatory_contributions, 'mandatory_contributions')
	},
	other_non_taxable: function(frm){
		total_non_taxable_compensation(frm, frm.doc.other_non_taxable, 'other_non_taxable')
	},

	// Net taxable reactivity
	less_taxable: function(frm){
		net_taxable_compensation(frm, frm.doc.less_taxable, 'less_taxable')
	},

	// Taxes withheld for remittance reactivity
	total_taxes_withheld: function(frm){
		taxes_withheld_for_remittance(frm, frm.doc.total_taxes_withheld, 'total_taxes_withheld')
	},
	add_less_adjustment: function(frm){
		taxes_withheld_for_remittance(frm, frm.doc.add_less_adjustment, 'add_less_adjustment')
	},

	// Total tax remittances made reactivity
	less_tax_remitted: function(frm){
		total_remittances_made(frm, frm.doc.less_tax_remitted, 'less_tax_remitted')
	},
	other_remittances_made: function(frm){
		total_remittances_made(frm, frm.doc.other_remittances_made, 'other_remittances_made')
	},

	// Tax still due reactivity, have to seperate.
	taxes_withheld_for_remittance: function(frm){
		tax_still_due(frm)
	},
	total_remittances_made: function(frm){
		tax_still_due(frm)
	},

	// Add: Penalties reactivity
	surcharge: function(frm){
		total_penalties(frm, frm.doc.surcharge, 'surcharge')
	},
	interest: function(frm){
		total_penalties(frm, frm.doc.interest, 'interest')
	},
	compromise: function(frm){
		total_penalties(frm, frm.doc.compromise, 'compromise')
	},
	total_penalties: function(frm){
		let total_amount_still_due = frm.doc.tax_still_due + frm.doc.total_penalties
		frm.set_value('total_amount_still_due', total_amount_still_due)
	},

	before_save: function (frm){
		if (!frm.doc.pres_rdo || frm.doc.pres_rdo.length < 3){
			frappe.throw("RDO Code is invalid.")
		}
	}

});
