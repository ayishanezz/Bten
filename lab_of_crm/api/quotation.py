import frappe
from frappe.utils import flt
from erpnext.selling.doctype.quotation.quotation import Quotation

class CustomQuotation(Quotation):
    def calculate_taxes_and_totals(self):
        # Step 1: Let ERPNext do normal calculations first
        super().calculate_taxes_and_totals()

        # Step 2: Add your additional items total
        additional_total = sum(flt(row.amount) for row in (self.custom_additional_items or []))
        self.custom_additional_total = additional_total or 0

        if additional_total:
            # Update net total
            self.net_total += additional_total
            self.base_net_total = self.net_total * (self.conversion_rate or 1)

            # --- Discount recalculation ---
            if self.additional_discount_percentage:
                discount_amount = self.net_total * (flt(self.additional_discount_percentage) / 100)
                self.discount_amount = discount_amount
            elif self.discount_amount:
                # percentage field might not be set, so recalc percentage from amount
                self.additional_discount_percentage = (self.discount_amount / self.net_total) * 100

            # Apply discount to net total for tax calculation
            total_after_discount = self.net_total - (self.discount_amount or 0)

            # --- Taxes recalculation ---
            total_taxes = 0
            for tax in self.taxes:
                if tax.charge_type == "On Net Total":
                    tax.tax_amount = total_after_discount * (flt(tax.rate) / 100)
                elif tax.charge_type == "Actual":
                    # keep the same amount already entered
                    pass
                total_taxes += tax.tax_amount or 0

            self.total_taxes_and_charges = total_taxes
            self.base_total_taxes_and_charges = total_taxes * (self.conversion_rate or 1)

            # --- Grand total recalculation ---
            self.grand_total = total_after_discount + self.total_taxes_and_charges
            self.base_grand_total = self.grand_total * (self.conversion_rate or 1)

            # --- Rounded values ---
            self.rounded_total = round(self.grand_total)
            self.base_rounded_total = round(self.base_grand_total)

        # Step 3: Payment terms will automatically use updated grand total
