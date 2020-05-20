# -*- coding: utf-8 -*-

from odoo import models


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"
    _order = "sequence, id"

