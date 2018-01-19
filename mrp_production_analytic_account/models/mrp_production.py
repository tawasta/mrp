# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Project',
        readonly=True,
        states={'confirmed': [('readonly', False)]}
    )

    @api.onchange('analytic_account_id')
    def onchange_project_id_update_locations(self):
        for record in self:
            if record.analytic_account_id and \
                    record.analytic_account_id.location_ids:
                location = record.analytic_account_id.location_ids[0]

                record.location_dest_id = location.id
                record.location_src_id = location.id