# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import UserError


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    def is_locked(self):
        """ Checks if line belongs to a locked BoM """
        for record in self:
            if record.bom_id.is_locked(record.bom_id):
                raise UserError(record.bom_id.locked_message)

    def display_locked_message(self, template):
        message = self.locked_message(template)
        raise Warning(message)

    @api.multi
    def write(self, values):
        """ Write triggers is_locked check for current BOM"""
        for record in self:
            record.is_locked()

        return super(MrpBomLine, self).write(values)
