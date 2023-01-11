frappe.listview_settings['BIR Form 2316'] = {
  set_actions_menu_items: function (listview) {
    listview.page.add_actions_menu_item(
      __('Download'),
      () => {
        const docs = listview.get_checked_items(true);

        frappe.call({
          method: 'erpnext_ph_payroll.erpnext_ph_payroll.download_bulk',
          args: {
            doctype: 'BIR Form 2316',
            docs,
          },
          callback: function (r) {
            if (!r.exc) {
              console.log(r.message);
            }
          }
        });
      },
      false
    );
  },
};
