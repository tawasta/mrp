from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    bsm_path = fields.Char(
        string="BSM Path", related="company_id.bsm_path", readonly=False
    )
