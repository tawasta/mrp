from odoo import fields, models


class MrpMove(models.Model):

    _inherit = "mrp.move"

    current_date = fields.Date(string="Scheduled Date")
