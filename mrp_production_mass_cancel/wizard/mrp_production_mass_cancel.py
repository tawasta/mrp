from odoo import _, api, exceptions, models


class MrpProductionMassCancel(models.TransientModel):

    _name = "mrp.production.mass.cancel"

    def get_cancellable_states(self):
        return ["confirmed"]

    @api.multi
    def confirm(self):

        prod_orders = self.env["mrp.production"].browse(
            self._context.get("active_ids"))

        allowed_states = self.get_cancellable_states()

        if any(s.state not in allowed_states for s in prod_orders):
            msg = _(
                "Please select only orders whose states " "allow cancelling"
            )
            raise exceptions.UserError(msg)

        for production in prod_orders:
            production.action_cancel()
