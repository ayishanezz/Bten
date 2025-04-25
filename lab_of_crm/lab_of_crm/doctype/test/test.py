# Copyright (c) 2025, Lab of Web and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class Test(Document):
    def before_insert(self):
        user_id = frappe.session.user
        doc_types = ["Lead", "Customer", "Sales Invoice"]
        total_file_size = 0
        total_doc_size = 0

        # 1. Calculate file size (owned or linked)
        file_docs = frappe.get_all(
            "File",
            fields=["file_size", "attached_to_doctype", "attached_to_name", "owner"]
        )

        for f in file_docs:
            file_size = f.file_size or 0
            if f.owner == user_id:
                total_file_size += file_size
                continue

            if f.attached_to_doctype and f.attached_to_name:
                try:
                    doc = frappe.get_doc(f.attached_to_doctype, f.attached_to_name)
                    if doc.owner == user_id:
                        total_file_size += file_size
                except:
                    pass

        # 2. Calculate size of owned documents
        for dt in doc_types:
            try:
                docs = frappe.get_all(dt, filters={"owner": user_id}, fields=["name"], limit=20)
                for d in docs:
                    try:
                        doc = frappe.get_doc(dt, d.name)
                        doc_dict = doc.as_dict()
                        doc_str = json.dumps(doc_dict)
                        total_doc_size += len(doc_str.encode("utf-8"))
                    except:
                        pass
            except:
                pass

        # 3. Combine sizes
        total_bytes = total_file_size + total_doc_size
        total_mb = round(total_bytes / (1024 * 1024), 2)

        # 4. Show message (or raise an error if over limit)
        frappe.msgprint(f"User '{user_id}' is using approximately {total_mb} MB of storage.")

        # Optional limit enforcement
        # if total_mb > 50:
        #     frappe.throw("You have exceeded your 50 MB storage limit.")
