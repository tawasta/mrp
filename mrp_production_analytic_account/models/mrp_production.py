# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )

    @api.onchange('project_id')
    def onchange_project_id_update_locations(self):
        for record in self:
            if record.project_id and record.project_id.location_ids:
                location = record.project_id.location_ids[0]

                record.location_dest_id = location.id
                record.location_src_id = location.id