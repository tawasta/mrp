from odoo import models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def button_mark_done(self):
        """When work orders are created, immediately go through each WO and
        simulate the click of "Start" and "Done"."""
        for work_order in self.workorder_ids:
            work_order.button_start()
            work_order.button_finish()
        super(MrpProduction, self).button_mark_done()
