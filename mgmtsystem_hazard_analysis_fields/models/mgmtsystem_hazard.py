from odoo import fields, models


class MgmtsystemHazard(models.Model):
    _inherit = "mgmtsystem.hazard"

    # Required in the form view only: the hazards that already exist have no location
    workcenter_category_id = fields.Many2one(
        "mrp.workcenter.category", string="Location", ondelete="restrict"
    )
    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        domain=lambda self: self._get_supplier_domain(),
    )

    def _get_supplier_domain(self):
        domain = [("is_company", "=", True), ("supplier_rank", ">", 0)]
        # The company of the suppliers is set in the settings of the company
        supplier_company = self.env.company.hazard_supplier_company_id
        if supplier_company:
            domain.append(("company_id", "=", supplier_company.id))
        return domain
