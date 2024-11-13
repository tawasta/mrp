from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    create_mrp_parameters_on_confirm = fields.Boolean(
        string="Create Product MRP Area Parameters on SO confirm",
        related="company_id.create_mrp_parameters_on_confirm",
        readonly=False,
        help="Select this to create Product MRP Area Parameters when confirming an order",
    )
