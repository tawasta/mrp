from odoo import models


class ReportMoOverview(models.AbstractModel):
    _inherit = "report.mrp.report_mo_overview"

    def _get_finished_operation_data(self, production, level=0, current_index=False):
        data = super()._get_finished_operation_data(
            production=production, level=level, current_index=current_index
        )

        operations = data.get("details", False)

        if operations:
            for index, workorder in enumerate(production.workorder_ids):
                operations[index]["mo_cost"] += workorder.purchase_cost

                quantity = 0

                for purchase in workorder.purchase_order_ids:
                    po_lines = purchase.order_line.filtered(
                        lambda line, workorder=workorder: line.product_id
                        == workorder.operation_id.purchase_product_id
                    )
                    for po_line in po_lines:
                        quantity += po_line.product_qty

                operations[index]["sub_uom_name"] = "{} {}".format(
                    quantity, workorder.purchase_product_id.uom_id.name
                )

        return data

    def _get_operations_data(self, production, level=0, current_index=False):
        data = super()._get_operations_data(
            production=production, level=level, current_index=current_index
        )

        operations = data.get("details", False)

        if operations:
            for index, workorder in enumerate(production.workorder_ids):
                operations[index]["mo_cost"] += workorder.purchase_cost

                quantity = 0

                for purchase in workorder.purchase_order_ids:
                    po_lines = purchase.order_line.filtered(
                        lambda line, workorder=workorder: line.product_id
                        == workorder.operation_id.purchase_product_id
                    )
                    for po_line in po_lines:
                        quantity += po_line.product_qty

                operations[index]["sub_uom_name"] = "{} {}".format(
                    quantity, workorder.purchase_product_id.uom_id.name
                )

            data["details"] = operations

        costs = 0

        for workorder in production.workorder_ids:
            costs += workorder.purchase_cost

        if data.get("summary", False) and "mo_cost" in data.get("summary").keys():
            data["summary"]["mo_cost"] += costs
        return data
