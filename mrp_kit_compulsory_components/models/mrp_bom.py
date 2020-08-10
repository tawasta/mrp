
from odoo import api, models, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    @api.constrains('bom_line_ids', 'type')
    def kit_bom_line_constrains(self):
        if self.type == 'phantom' and not self.bom_line_ids:
            raise ValidationError(_("Kit has to contain at least one product."))

    @api.model
    def create(self, vals):
        if vals.get('type') == 'phantom' and not vals.get('bom_line_ids'):
            raise ValidationError(_("Kit has to contain at least one product."))

        return super(MrpBom, self).create(vals)
