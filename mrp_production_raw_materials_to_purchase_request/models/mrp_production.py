from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    def check_material_for_request(self, material):
        ''' Set conditions when the material should be suggested to
        be included in the purchase request.  '''
        buy_route = self.env.ref('purchase.route_warehouse0_buy',
                                 raise_if_not_found=False)
        if not buy_route:
            raise UserError(_("'Buy' route not found in the system."))

        # If the core's Buy route is checked for the product, the product is
        # stockable, and there is not enough qty available,
        # request the product to be purchased
        if buy_route.id in [r.id for r in material.product_id.route_ids] \
                and self._get_material_qty(material) > 0 \
                and material.product_id.type == 'product':
            return True
        else:
            return False

    def _get_material_qty_for_request(self, material):
        ''' Set how much of the material should be requested to
        be purchased '''
        return material.product_uom_qty - material.quantity_available

    @api.multi
    def create_purchase_request(self):
        ''' Creates a new purchase request containing the missing raw
        materials '''
        self.ensure_one()

        purchase_request_model = self.env['purchase.request']
        purchase_request_line_model = self.env['purchase.request.line']

        vals = {
            'mrp_production_id': self.id,
            'requested_by': self.env.uid,
            'origin': self.name,
            'description': u'%s %s' % (_('Materials for'), self.name),
            'stock_location_id': self.location_src_id.id
        }

        # Check if mrp_production_analytic_account is installed
        if hasattr(self, 'analytic_account_id'):
            vals['analytic_account_id'] = self.analytic_account_id.id

        res = purchase_request_model.create(vals)

        for material in self.move_raw_ids:
            if self.check_material_for_request(material):
                pr_line_vals = {
                    'product_id': material.product_id.id,
                    'product_uom_id': material.product_uom.id,
                    'product_qty':
                        self._get_material_qty_for_request(material),
                    'name': material.product_id.name,
                    'request_id': res.id,
                }

                if hasattr(self, 'analytic_account_id'):
                    vals['analytic_account_id'] = self.analytic_account_id.id

                purchase_request_line_model.create(pr_line_vals)

        return {
            'name': u'%s / Purchase Request' % self.name,
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'purchase.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': res.id,
        }

    purchase_request_ids = fields.One2many(
        comodel_name='purchase.request',
        inverse_name='mrp_production_id',
        string='Purchase Requests',
    )
