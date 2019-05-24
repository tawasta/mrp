from odoo import fields, models


class MrpConfigSettings(models.TransientModel):

    _inherit = 'mrp.config.settings'

    bom_cost_calculation_method = fields.Selection(
        related='company_id.bom_cost_calculation_method',
        help='''What should be used when calculating BOM component costs''')
