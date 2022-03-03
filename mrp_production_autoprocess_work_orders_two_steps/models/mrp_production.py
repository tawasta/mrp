from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    work_orders_processed = fields.Boolean(default=False, copy=False)

    @api.multi
    def button_plan_start_work_orders(self):
        """ Goes through each Work Order and starts them, respectively. """
        self.button_plan()
        for work_order in self.workorder_ids:
            work_order.button_start()

    @api.multi
    def button_plan_process_work_orders(self):
        """ Marks each Work Order to Done. """
        for work_order in self.workorder_ids:
            work_order.record_production()
        # This helper field decides if this function's
        # related button is shown
        self.work_orders_processed = True

    @api.multi
    def action_cancel(self):
        """ Cancels all Work Orders and only after that
        a manufacturing order will be cancelled. """
        for work_order in self.workorder_ids:
            work_order.action_cancel()
        super().action_cancel()
