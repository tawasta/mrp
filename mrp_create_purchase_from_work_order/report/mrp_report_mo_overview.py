from odoo import models


class ReportMoOverview(models.AbstractModel):
    _inherit = "report.mrp.report_mo_overview"

    def _get_bom_operation_cost(self, workorder, production, kit_operation=False):
        cost = super()._get_bom_operation_cost(
            workorder=workorder, production=production, kit_operation=kit_operation
        )
        cost += workorder.purchase_cost
        return cost

    def _get_finished_operation_data(self, production, level=0, current_index=False):
        data = super()._get_finished_operation_data(
            production=production, level=level, current_index=current_index
        )

        operations = data.get("details", False)

        if operations:
            for index, workorder in enumerate(production.workorder_ids):
                quantity = 0

                for purchase in workorder.purchase_order_ids:
                    po_lines = purchase.order_line.filtered(
                        lambda line, workorder=workorder: line.product_id
                        == workorder.operation_id.purchase_product_id
                        or line.product_id
                        == workorder.workcenter_id.default_purchase_product_id
                    )
                    for po_line in po_lines:
                        quantity += po_line.product_qty

                operations[index]["sub_uom_name"] = (
                    f"{quantity} {workorder.purchase_product_id.uom_id.name}"
                )

        return data

    def _get_operations_data(self, production, level=0, current_index=False):
        data = super()._get_operations_data(
            production=production, level=level, current_index=current_index
        )

        operations = data.get("details", False)

        if operations:
            for index, workorder in enumerate(production.workorder_ids):
                quantity = 0

                for purchase in workorder.purchase_order_ids:
                    po_lines = purchase.order_line.filtered(
                        lambda line, workorder=workorder: line.product_id
                        == workorder.operation_id.purchase_product_id
                        or line.product_id
                        == workorder.workcenter_id.default_purchase_product_id
                    )
                    for po_line in po_lines:
                        quantity += po_line.product_qty

                uom_name = (
                    workorder.purchase_product_id.uom_id.name
                    or workorder.workcenter_id.default_purchase_product_id.uom_id.name
                )
                if quantity and uom_name:
                    operations[index]["sub_uom_name"] = f"{quantity} {uom_name}"

            data["details"] = operations

        return data
