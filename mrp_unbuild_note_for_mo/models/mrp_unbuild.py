from odoo import models


class MrpUnbuild(models.Model):

    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        res = super().action_unbuild()

        self.mo_id.unbuild_note = "unbuilt"

        return res
