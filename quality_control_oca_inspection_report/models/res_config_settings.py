from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    qc_inspection_report_title = fields.Char(
        related="company_id.qc_inspection_report_title",
        string="Inspection Report: Title",
        readonly=False,
    )

    qc_inspection_report_product_section_title = fields.Char(
        related="company_id.qc_inspection_report_product_section_title",
        string="Inspection Report: Product Information Section Title",
        readonly=False,
    )

    qc_inspection_report_inspection_section_title = fields.Char(
        related="company_id.qc_inspection_report_inspection_section_title",
        string="Inspection Report: Inspection Information Section Title",
        readonly=False,
    )

    qc_inspection_report_trim_decimals = fields.Boolean(
        related="company_id.qc_inspection_report_trim_decimals",
        string="Inspection Report: Trim Trailing Decimals",
        readonly=False,
    )
