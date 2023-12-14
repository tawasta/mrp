from odoo import fields, models


class OpenProductReportWizard(models.TransientModel):

    _name = "open.product.report.wizard"

    number_of_days = fields.Integer(string="Days", required=True, default=0)

    def forecast_open_report(self):
        self.env.ref("mrp_multi_level_inventory_qty.view_product_report_pivot").id

        ctx = dict(self._context, number_of_days=self.number_of_days)
        self.env["product.report"].with_context(ctx).init()

        return {
            "name": "Product circulation report",
            "type": "ir.actions.act_window",
            "res_model": "product.report",
            "view_type": "pivot",
            "view_mode": "pivot",
            "context": ctx,
        }
