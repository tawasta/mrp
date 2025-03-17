from odoo import api, models


class MrpReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_operation_line(self, product, bom, qty, level, index):
        operations = super()._get_operation_line(product, bom, qty, level, index)

        for operation in operations:
            uom_name = operation.get("uom_name", False)
            operation["uom_name"] = uom_name and "{}".format("mm:ss")

        return operations
