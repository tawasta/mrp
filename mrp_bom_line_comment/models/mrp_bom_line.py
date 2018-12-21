# -*- coding: utf-8 -*-
from odoo import fields, models


class MrpBom(models.Model):

    _inherit = "mrp.bom.line"

    comment = fields.Char(
        string='Comment',
        help='A free comment. Has no functional purpose on manufacturing',
    )
