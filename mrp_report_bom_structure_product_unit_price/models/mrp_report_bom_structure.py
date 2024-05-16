from odoo import api, models


class MrpReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        parent_product,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        data = super()._get_component_data(
            parent_bom=parent_bom,
            parent_product=parent_product,
            warehouse=warehouse,
            bom_line=bom_line,
            line_quantity=line_quantity,
            level=level,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
        )

        if bom_line:
            data["unit_price"] = bom_line.product_id.standard_price

        return data

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        parent_product=False,
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        data = super()._get_bom_data(
            bom=bom,
            warehouse=warehouse,
            product=product,
            line_qty=line_qty,
            bom_line=bom_line,
            level=level,
            parent_bom=parent_bom,
            parent_product=parent_product,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
        )

        data["unit_price"] = data.get("prod_cost", 0)

        return data
