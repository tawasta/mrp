from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    @api.multi
    def calculate_component_cost(self):
        ''' Returns the cost of the BOM line, using either
        -the cost price of the line's product, or
        -the price of the product's primary supplier
        ...converted to the UoM used on the line (with also currency rate
        conversion if the vendor uses a different currency)'''

        # This should be run for one record at tht time, as it returns
        # the component cost
        self.ensure_one()

        if self.bom_id.company_id.bom_cost_calculation_method \
                == 'vendor_price':
            # Use primary vendor's price, fall back to 0 if no vendor exists
            if not self.product_id.seller_ids:
                cost = 0.00
            else:
                primary_vendor = self.product_id.seller_ids[0]

                # Calculate unit cost in primary currency
                unit_cost_in_eur \
                    = self.env['res.currency'] \
                    ._compute(primary_vendor.currency_id,
                              self.currency_id,
                              primary_vendor.price)

                # Calculate cost for the unit used on the BOM.
                # Note the use of purchase unit of measure instead of
                # regular uom
                cost = self.product_id.uom_po_id._compute_price(
                    unit_cost_in_eur, self.product_uom_id
                )
        else:
            # Use product's standard_price field
            cost = self.product_id.uom_id._compute_price(
                self.product_id.standard_price, self.product_uom_id
            )

        return cost

    @api.multi
    def _get_component_cost_total(self):
        for line in self:
            line.component_cost_total = line.component_cost * line.product_qty

    @api.multi
    def _get_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([],
                                                                 limit=1,
                                                                 order="id")
        for line in self:
            line.currency_id = line.bom_id.company_id.sudo().currency_id.id \
                or main_company.currency_id.id

    component_cost = fields.Float(
        string="Component Cost per Unit",
        digits=dp.get_precision('Product Price'),
        help='''Component cost for 1 BOM line item'''
    )

    component_cost_total = fields.Float(
        compute=_get_component_cost_total,
        string="Total Component Cost",
        digits=dp.get_precision('Product Price')
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute=_get_currency_id,
        string='Currency'
    )
