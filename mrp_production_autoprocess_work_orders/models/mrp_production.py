from odoo import api, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def button_plan(self):
        '''When work orders are created, immediately go through each WO and
        simulate the click of "Start working" and "Done".'''
        super(MrpProduction, self).button_plan()
        for work_order in self.workorder_ids:
            work_order.button_start()
            work_order.record_production()
