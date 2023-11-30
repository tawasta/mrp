from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    minutes_in_year = fields.Integer(string="Minutes in a year")
