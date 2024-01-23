from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    time_in_year = fields.Integer(string="Seconds in a year")
