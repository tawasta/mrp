# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    @api.depends('bom_line_ids')
    def _compute_has_subassemblies(self):
        for bom in self:
            if any([l.child_bom_id for l in bom.bom_line_ids]):
                bom.has_subassemblies = True
            else:
                bom.has_subassemblies = False

    has_subassemblies = fields.Boolean(
        compute=_compute_has_subassemblies,
        string='Contains subassemblies',
        store=True,
    )
