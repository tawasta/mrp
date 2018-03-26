# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    def iterate_children(self, top_bom_id, bom_lines):

        archived_product_line_model = \
            self.env['mrp_bom_archived_product_list.archived_product_line']

        ''' Go through the BOM recursively and search for products that
        have been marked as archived'''

        for line in bom_lines:
            self.iterate_children(top_bom_id, line.child_line_ids)
            if not line.product_id.active:
                archived_product_line_model.create({
                    'bom_id': top_bom_id,
                    'product_id': line.product_id.id,
                    'parent_id': line.bom_id.id,
                })

    @api.multi
    def refresh_archive_info(self):
        self.ensure_one()
        self.archived_product_line_ids = False
        self.iterate_children(self.id, self.bom_line_ids)
        self.archived_info_last_update = fields.datetime.now()

    archived_info_last_update = fields.Datetime(
        string='Archived info last updated',
    )

    archived_product_line_ids = fields.One2many(
        comodel_name='mrp_bom_archived_product_list.archived_product_line',
        inverse_name='bom_id',
        string='Archived Products on BOM',
    )
