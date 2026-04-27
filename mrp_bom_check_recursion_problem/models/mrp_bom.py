import logging
from collections import defaultdict

from odoo import _, fields, models
from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def cron_recursion_check_bom_cycle(self):
        """Checks if some BoMs have a recursion problem."""
        boms = self.env["mrp.bom"].search([]).ids
        batch_boms = list()
        interval = 50
        for x in range(0, len(boms), interval):
            batch_boms.append(boms[x : x + interval])

        for batch in batch_boms:
            job_desc = _(f"Check recursion problems of BoMs: {batch}")
            self.with_delay(description=job_desc).recursion_check_bom_cycle(batch)

        _logger.info("Cron Compute BoM values completed")

    def recursion_check_bom_cycle(self, batch):
        check_boms = self.env["mrp.bom"].search([("id", "in", batch)])
        subcomponents_dict = dict()

        def _check_cycle(components, finished_products):
            products_to_find = self.env["product.product"]

            for component in components:
                if component in finished_products:
                    names = finished_products.mapped("display_name")
                    recursion_log = self.env["recursion.mrp.bom.log"]
                    log_values = {
                        "name": fields.fields.Datetime.now(),
                        "problem_products": names,
                    }
                    recursion_log.create(log_values)
                if component not in subcomponents_dict:
                    products_to_find |= component

            bom_find_result = self._bom_find(products_to_find)
            for component in components:
                if component not in subcomponents_dict:
                    bom = bom_find_result[component]
                    subcomponents = bom.bom_line_ids.filtered(
                        lambda line, component=component: not line._skip_bom_line(
                            component
                        )
                    ).product_id
                    subcomponents_dict[component] = subcomponents
                subcomponents = subcomponents_dict[component]
                if subcomponents:
                    _check_cycle(subcomponents, finished_products | component)

        # boms_to_check = self
        boms_to_check = check_boms
        for bom_check in check_boms:
            domain = []
            for product in bom_check.bom_line_ids.product_id:
                domain = OR([domain, self._bom_find_domain(product)])
            if domain:
                boms_to_check |= self.env["mrp.bom"].search(domain)

        # for bom in boms_to_check:
        for bom in check_boms:
            if not bom.active:
                continue
            finished_products = (
                bom.product_id or bom.product_tmpl_id.product_variant_ids
            )
            if bom.bom_line_ids.bom_product_template_attribute_value_ids:
                grouped_by_components = defaultdict(lambda: self.env["product.product"])
                for finished in finished_products:
                    components = bom.bom_line_ids.filtered(
                        lambda line, finished=finished: not line._skip_bom_line(
                            finished
                        )
                    ).product_id
                    grouped_by_components[components] |= finished
                for components, finished in grouped_by_components.items():
                    _check_cycle(components, finished)
            else:
                _check_cycle(bom.bom_line_ids.product_id, finished_products)
