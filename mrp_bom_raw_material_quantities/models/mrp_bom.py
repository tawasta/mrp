from odoo import api, models


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    @api.multi
    def compute_raw_material_qties(self, raw_mats_needed=None, multiplier=1):
        '''Returns a dictionary with total number of raw materials required to
        manufacture the products of the BOMs. Iterates through subassemblies
        and takes into account how many subassemblies are needed for the main
        assembly when calculating their number of components needed '''

        if raw_mats_needed is None:
            raw_mats_needed = []

        for bom in self:
            if not bom.bom_line_ids:
                return raw_mats_needed

            for line in bom.bom_line_ids:
                product = line.product_id
                # Do a unit conversion from the UoM used on the BOM line to the
                # default UoM of the product.
                qty_in_uom = \
                    line.product_uom_id\
                    ._compute_quantity(
                        line.product_qty,
                        product.uom_id)

                buy_route = self.env.ref(
                    'purchase.route_warehouse0_buy',
                    raise_if_not_found=False)

                if not line.child_bom_id or buy_route in\
                        line.product_id.route_ids:
                    # If the product on the line is
                    # a) a raw material
                    # b) a purchasable with a BOM,
                    # either add it to the list as a new product or increase
                    # the qty if it already exists
                    product_index = next(
                        (i for (i, d) in enumerate(raw_mats_needed)
                            if d['product'] == product), None)

                    if product_index is None:
                        raw_mats_needed.append({
                            'product': product,
                            'quantity': qty_in_uom * multiplier,
                        })
                    else:
                        raw_mats_needed[product_index]['quantity'] += \
                            qty_in_uom * multiplier
                else:
                    # If the product on the line is not a raw material but has
                    # a bom, iterate its lines recursievely
                    line.child_bom_id.compute_raw_material_qties(
                        raw_mats_needed,
                        multiplier*qty_in_uom)

        return raw_mats_needed
