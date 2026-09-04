from odoo import models
from odoo.tools import float_round, formatLang


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    def _report_format_quantitative_value(self, trim=False):
        """Locale-formatted quantitative value for the PDF report.

        With trim=True, (the company's qc_inspection_report_trim_decimals
        setting), insignificant trailing zeros are dropped
        """
        self.ensure_one()
        max_digits = self.env["decimal.precision"].precision_get("Quality Control")
        digits = max_digits
        if trim:
            rounded = float_round(self.quantitative_value, precision_digits=max_digits)
            text = f"{rounded:.{max_digits}f}".rstrip("0").rstrip(".")
            digits = len(text.split(".", 1)[1]) if "." in text else 0
        return formatLang(self.env, self.quantitative_value, digits=digits)
