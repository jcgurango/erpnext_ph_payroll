import frappe
from io import BytesIO
import os
import zipfile
import time

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
