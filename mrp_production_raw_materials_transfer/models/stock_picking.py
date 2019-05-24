from odoo import fields, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    material_transfer_production_id = fields.Many2one(
        string='Manufacturing Order',
        comodel_name='mrp.production',
        help='''Manufacturing Order this Raw Material Transfer is related to'''
    )
