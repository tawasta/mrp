# -*- coding: utf-8 -*-
from odoo import api, models


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    @api.multi
    def write(self, values):
        """ Write triggers a locked check for current BOM """
        for record in self:
            bom_id = record.bom_id
            if bom_id.locked or bom_id.parent_locked:
                bom_id.display_locked_error()

        return super(MrpBomLine, self).write(values)
