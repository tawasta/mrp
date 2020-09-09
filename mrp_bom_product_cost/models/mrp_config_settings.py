from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    def _get_bom_cost_calc_methods(self):
        return [('cost_price', 'Cost Price'),
                ('vendor_price', "Primary Vendor's Price")]

    bom_cost_calculation_method = fields.Selection(
        selection=_get_bom_cost_calc_methods,
        default='cost_price',
        string='BOM Cost Calculation Method',
        help='''What should be used when calculating BOM component costs''')
