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
