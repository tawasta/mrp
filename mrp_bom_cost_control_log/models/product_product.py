from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    compute_control_logs = fields.Boolean(
        related="product_tmpl_id.compute_control_logs"
    )
    mrp_control_log_ids = fields.One2many(
        "mrp.control.log", "product_id", string="BoM cost logs"
    )
    mrp_control_log_count = fields.Integer(
        string="# BoM cost logs",
        compute=lambda self: self._compute_mrp_control_log_count(),
    )

    @api.depends("mrp_control_log_ids")
    def _compute_mrp_control_log_count(self):
        for product in self:
            product.mrp_control_log_count = len(product.mrp_control_log_ids.ids)

    def _compute_bom_price(self, bom, boms_to_recompute=False):
        cost = super()._compute_bom_price(bom, boms_to_recompute=boms_to_recompute)

        if self.compute_control_logs:
            mrp_control_log_model = self.env["mrp.control.log"]

            log_vals = {
                "name": "{} / {}".format(self.name, fields.datetime.now()),
                "product_code": self.default_code,
                "computed_date": fields.datetime.now(),
                "computed_cost": cost,
                "product_id": self.id,
            }

            mrp_control_log_model.create(log_vals)

        return cost

    def action_product_bom_cost_log(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_bom_cost_control_log.action_mrp_cost_logs"
        )
        action["domain"] = [("product_id", "=", self.id)]
        return action
