from odoo import fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    work_orders_processed = fields.Boolean(default=False, copy=False)

    def button_plan_start_work_orders(self):
        """Goes through each Work Order and starts them, respectively."""
        self.button_plan()
        for work_order in self.workorder_ids:
            work_order.button_start()

    def action_cancel(self):
        """Cancels all Work Orders and only after that
        a manufacturing order will be cancelled."""
        for work_order in self.workorder_ids:
            work_order.action_cancel()
        return super(MrpProduction, self).action_cancel()

    def button_mark_done(self):
        # Marks each Work Order to Done
        for work_order in self.workorder_ids:
            work_order.record_production()
        # This helper field decides if button_plan_start_work_orders
        # function's related button is shown
        self.work_orders_processed = True
        return super(MrpProduction, self).button_mark_done()
