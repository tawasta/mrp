from odoo import models


class MrpReportBomStructure(models.AbstractModel):

    _inherit = "report.mrp.report_bom_structure"

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):

        components, total = super()._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )

        for component in components:
            prod = component.get("prod_id", 0)
            if prod:
                product_id = self.env["product.product"].search([("id", "=", prod)])
                component.update({"unit_price": product_id.standard_price})

        return components, total
