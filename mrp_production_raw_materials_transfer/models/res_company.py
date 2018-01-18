# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions


class ResCompany(models.Model):

    _inherit = 'res.company'

    raw_materials_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Raw Materials Transfer Picking Type',
        domain=[('code', '=', 'internal')],
        help='''Used when transferring raw materials required by a MO''')

    raw_materials_src_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Raw Materials Source Location',
        domain=[('usage', '=', 'internal')],
        help='''Used when transferring raw materials required by a MO''')