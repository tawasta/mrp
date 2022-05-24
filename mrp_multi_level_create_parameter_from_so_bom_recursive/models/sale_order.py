
from odoo import api, models
from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def get_searchable_products(self, line):

        bom_model = self.env['mrp.bom']
        products = self.env['product.product']
        products |= line.product_id

        def get_sub_lines(current_bom, product_variant=False):
            """ Returns a recordset of products of all the possible components
            from all the BoMs, listed recursively, based on the product on sale
            order line. The product's variant and its attributes are taken into
            account when listing the components. No duplicate records are
            returned because of the union set operator '|'. """

            products = self.env['product.product']
            # BoM's product is also added to the list
            products |= current_bom.product_id

            for bom_line in current_bom.bom_line_ids:
                product_id = bom_line.product_id

                # Check if BoM line's attributes match with the product's
                # attributes, or if there are any attributes.
                if (bom_line.attribute_value_ids.ids and
                        not all(attr in product_variant.attribute_value_ids.ids
                        for attr in bom_line.attribute_value_ids.ids)):
                    continue

                if not bom_line.child_bom_id:
                    products |= product_id

                else:
                    # Go through the child BoM also
                    child_bom = product_id.bom_ids and product_id.bom_ids[0]
                    products |= get_sub_lines(child_bom, product_id)

            return products

        # This will get only one BoM, so singleton error is avoided
        bom = bom_model._bom_find(product_tmpl=line.product_id.product_tmpl_id,
                                  product=line.product_id)

        if bom:
            products |= get_sub_lines(bom, line.product_id)

        return products

    def prepare_product_mrp_area_vals(self, product):
        """ Default Product Mrp Area values """
        return {
            "mrp_area_id": 1,
            "product_id": product.id,
        }

    def mrp_area_search_domain(self, product):
        """ Search domain of Product Mrp Area records """

        # Search also archived records to avoid unique error
        return [('product_id', '=', product.id), '|',
                ('active', '=', True), ('active', '=', False)]

    def product_mrp_area_create_multi(self, products):

        product_mrp_area_model = self.env['product.mrp.area']

        for prod in products:
            domain = self.mrp_area_search_domain(prod)
            parameters = product_mrp_area_model.sudo().search(domain)

            if not parameters and prod.type in ['consu', 'product']:
                values = self.prepare_product_mrp_area_vals(prod)

                # Creates Product Mrp Area record
                product_mrp_area_model.sudo().create(values)

    @api.multi
    @job
    def product_mrp_area_create_multi_queued(self, line):
        products = self.get_searchable_products(line)
        self.product_mrp_area_create_multi(products)
        return_text = "Tried to create MRP Area Parameters from Sale Order line {}"\
                      " and Order {}".format(line.name, line.order_id.name)
        return return_text

    @api.multi
    @job
    def _product_mrp_area_create_multi_queued(self, lines):
        for line in lines:
            job_desc = "Create MRP Area Parameters from Sale Order line: {}"\
                        .format(line.name)
            self.with_delay(description=job_desc)\
                        .product_mrp_area_create_multi_queued(line)

    @api.multi
    def action_confirm(self):
        res = super().action_confirm()
        job_desc = "Begin MRP Area Parameters creation"
        self.with_delay(description=job_desc)\
                    ._product_mrp_area_create_multi_queued(self.order_line)

        return res
