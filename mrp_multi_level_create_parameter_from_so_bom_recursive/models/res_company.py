from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    create_mrp_parameters_on_confirm = fields.Boolean(
        string="Create Product MRP Area Parameters on SO confirm"
    )
