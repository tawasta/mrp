# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions


class MrpConfigSettings(models.TransientModel):

    _inherit = 'mrp.config.settings'

    raw_materials_picking_type_id = fields.Many2one(
        related='company_id.raw_materials_picking_type_id',
        string='Raw Materials Transfer Picking Type')

    raw_materials_src_location_id = fields.Many2one(
        related='company_id.raw_materials_src_location_id',
        string='Raw Materials Default Source Location')