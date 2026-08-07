from odoo import models


class ProductTemplateCreateMrpParameter(models.Model):
    _name = "product.template.create.mrp.parameter"
    _description = "Product template Create Mrp Parameter"

    def prepare_product_mrp_area_vals(self, product, company_id):
        """Default Product Mrp Area values"""

        area = self.env["mrp.area"].search(
            [("company_id", "=", company_id.id)], limit=1
        )

        return {
            "mrp_area_id": area.id,
            "product_id": product.id,
        }

    def mrp_area_search_domain(self, product, company_id):
        """Search domain of Product Mrp Area records"""

        # Search also archived records to avoid unique error
        return [
            ("product_id", "=", product.id),
            "|",
            ("active", "=", True),
            ("active", "=", False),
            ("company_id", "=", company_id.id),
        ]

    def _product_mrp_area_create_multi(self, product, company_id, product_types=False):
        product_mrp_area_model = self.env["product.mrp.area"]
        product_types = product_types or ["consu"]

        domain = self.mrp_area_search_domain(product, company_id)
        parameters = product_mrp_area_model.sudo().search(domain)

        if not parameters and product.type in product_types:
            values = self.prepare_product_mrp_area_vals(product, company_id)

            # Creates Product Mrp Area record
            product_mrp_area_model.sudo().create(values)

    def action_mass_create_product_mrp_parameter(self, use_cron=False):
        if not use_cron:
            product_tmpls = self.env["product.template"].browse(
                self._context.get("active_ids")
            )
        else:
            product_tmpls = self.env["product.template"].search([], limit=99999)

        ir_config_model = self.env["ir.config_parameter"]

        product_types = (
            ir_config_model.sudo().get_param("create_product_mrp_area_product_types")
            or False
        )

        for product_tmpl in product_tmpls:
            # MRP Area is company dependent
            company_id = product_tmpl.company_id or self.env.company

            area_exists = self.env["mrp.area"].search(
                [("company_id", "=", company_id.id)]
            )

            # No "Break" because products can have multiple companies
            if not area_exists:
                continue

            # It is possible that a template has a massive amount of variants
            for product in product_tmpl.product_variant_ids:
                job_desc = (
                    f"Create MRP Area Parameter for product: {product.display_name}"
                )
                self.with_delay(description=job_desc)._product_mrp_area_create_multi(
                    product, company_id, product_types
                )
