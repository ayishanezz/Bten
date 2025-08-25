import frappe

def execute():
    # Reload Print Format so frappe.new_doc knows the latest fields
    frappe.reload_doc("core", "doctype", "print_format")
    
    if not frappe.db.exists("Custom Field", "Print Format-company"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Print Format",
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "insert_after": "disabled",
            "reqd": 0
        }).insert(ignore_permissions=True)
        frappe.clear_cache(doctype="Print Format")


