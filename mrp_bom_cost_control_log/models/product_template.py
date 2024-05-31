from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    compute_control_logs = fields.Boolean(string="Compute BoM cost logs")
