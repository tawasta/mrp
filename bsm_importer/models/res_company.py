from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bsm_path = fields.Char("BSM Path")
