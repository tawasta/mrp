from odoo import fields, models


class OpenProductReportWizard(models.TransientModel):

    _name = "open.product.report.wizard"

    number_of_days = fields.Integer(string="Days", required=True, default=0)
    product_category_id = fields.Many2one("product.category", string="Product Category")
    product_id = fields.Many2one("product.product", "Product")
    abc_profile_id = fields.Many2one(
        "abc.classification.profile", "ABC Classification Profile"
    )
    abc_level_id = fields.Many2one(
        "abc.classification.profile.level",
        "ABC Classification Level",
    )

    def forecast_open_report(self):
        self.env.ref("mrp_multi_level_inventory_qty.view_product_report_pivot").id

        ctx = dict(
            self._context,
            number_of_days=self.number_of_days,
            product_category_id=self.product_category_id.id,
            product_id=self.product_id.id,
            abc_profile_id=self.abc_profile_id.id,
            abc_level_id=self.abc_level_id.id,
        )
        self.env["product.report"].with_context(ctx).init()

        return {
            "name": "Inventory Turnover report",
            "type": "ir.actions.act_window",
            "res_model": "product.report",
            "view_type": "pivot",
            "view_mode": "pivot",
            "context": ctx,
            "target": "main",
        }
