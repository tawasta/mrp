# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    material_transfer_production_id = fields.Many2one(
        string='Manufacturing Order',
        comodel_name='mrp.production',
        help='''Manufacturing Order this Raw Material Transfer is related to'''
    )