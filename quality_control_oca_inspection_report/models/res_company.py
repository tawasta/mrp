from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    qc_inspection_report_title = fields.Char(
        string="Inspection Report Title",
        default="Inspection",
        translate=True,
    )

    qc_inspection_report_product_section_title = fields.Char(
        string="Product Information Section Title",
        default="Product Information",
        translate=True,
    )

    qc_inspection_report_inspection_section_title = fields.Char(
        string="Inspection Information Section Title",
        default="Inspection Information",
        translate=True,
    )

    qc_inspection_report_trim_decimals = fields.Boolean(
        string="Trim Trailing Decimals on Inspection Report",
        help="On the inspection PDF report, drop insignificant trailing zeros "
        "from quantitative result values (e.g. show 12.3 instead of 12.30000).",
    )
