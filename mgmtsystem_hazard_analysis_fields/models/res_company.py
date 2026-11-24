from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    hazard_supplier_company_id = fields.Many2one(
        "res.company",
        string="Supplier company",
        help="The supplier of a hazard is selected from the supplier companies "
        "that belong to this company. If empty, the suppliers of all the "
        "companies are listed.",
    )
