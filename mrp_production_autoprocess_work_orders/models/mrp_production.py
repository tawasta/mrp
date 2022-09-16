from odoo import models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def button_mark_done(self):
        """When work orders are created, immediately go through each WO and
        simulate the click of "Start" and "Done"."""

        # If there are no work orders, create them
        if not self.workorder_ids:
            self._create_workorder()

        for work_order in self.workorder_ids:
            # Set WO's Quantity To Be Produced to be
            # the same as MO's Quantity Producing. This
            # is needed if less products were produced.
            work_order.qty_remaining = self.qty_producing

            work_order.button_start()
            work_order.button_finish()

        # Set Quantity To Produce to be the same as Quantity Producing.
        # This means that if less products were produced, then a
        # manufacturing order is set to Done.
        self.product_qty = self.qty_producing
        super(MrpProduction, self).button_mark_done()
