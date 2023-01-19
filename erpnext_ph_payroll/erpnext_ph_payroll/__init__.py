import frappe
from io import BytesIO
import zipfile

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
  form_fill_template = frappe.get_doc('Form Fill Template', form_template.get_form_fill_template())
  form_fill_data = form_fill_template.fill_document(form_template.get_form_fill_data())
  frappe.response['type'] = 'pdf'
  frappe.response['filename'] = 'preview.pdf'
  frappe.response['filecontent'] = form_fill_data
