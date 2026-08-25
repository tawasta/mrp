from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    serial_number = fields.Char(
        string="Serial Number / Identifier",
        help=(
            "Freetext identifier to help you find inspections related to a "
            "particular serial number or other identifier. Not connected "
            "to Odoo's own serial number / lot tracking."
        ),
    )
