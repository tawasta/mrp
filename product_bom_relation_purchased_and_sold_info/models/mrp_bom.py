from odoo import fields, models


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    bom_rel_purchase_count = fields.Integer(
        string="Reserved purchase qty",
        compute="_compute_bom_rel_purchase_and_sold_count",
    )

    bom_rel_sold_count = fields.Integer(
        string="Reserved sale qty", compute="_compute_bom_rel_purchase_and_sold_count"
    )

    def _compute_bom_rel_purchase_and_sold_count(self):
        product_id = self._context.get("active_id")
        product_model = self._context.get("active_model")
        if product_model in ["product.product", "product.template"]:
            product = self.env[product_model].search([("id", "=", product_id)])
            product = product.product_variant_id or product
            stock_moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", product.id),
                    ("picking_id.state", "in", ["confirmed", "assigned"]),
                ]
            )

            bom_lines = self.env["mrp.bom.line"].search(
                [("product_id", "=", product.id)]
            )

            for line in bom_lines:
                line.bom_id.bom_rel_purchase_count = sum(
                    [x.reserved_availability for x in stock_moves if x.purchase_line_id]
                )
                line.bom_id.bom_rel_sold_count = sum(
                    [x.reserved_availability for x in stock_moves if x.sale_line_id]
                )
