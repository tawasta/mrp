from odoo import models, api, exceptions, _
import re


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def create_revision(self):
        """
        Create new revision. Not implemented on products with variants

        1. Try to get new revision number by product suffix
        2. Duplicate product
        3. Deactivate old product
        """

        self.ensure_one()

        if self.product_variant_count > 1:
            msg = _("Revisioning products with variants is not allowed")
            raise exceptions.UserError(msg)

        default_code = self.get_next_revision_number(self.default_code)

        # Create a copy of the current product, mark it as active in case the
        # old one was not
        new_product = self.copy({"name": self.name, "default_code": default_code,})
        new_product.active = True

        if new_product.default_code != default_code:
            # Default code can get ignored/overridden (?)
            new_product.default_code = default_code

        self.message_post(
            body=_("Created a new revision '%s'") % new_product.display_name
        )

        new_product.message_post(
            body=_("Created a new revision from '%s'") % self.display_name
        )

        # Archive the current product
        self.active = False

        view_action = {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "form",
            "view_type": "form",
            "res_id": new_product.id,
            "views": [(False, "form")],
            "target": "current",
        }

        return view_action

    def get_next_revision_number(self, code):
        """
        Get next revision number
        Only supports suffix ending in numbers only

        e.g.
        - PR-123 becomes PR-124
        - P456 becomes P457
        """
        if not code:
            return False

        suffix_re = "[0-9]+$"

        if re.search(suffix_re, code):
            sequence = re.search(suffix_re, code).group()
            new_sequence = str(int(sequence) + 1).zfill(len(sequence))

            return re.sub(suffix_re, new_sequence, code)

        return False

    def action_create_revision(self):
        """
        Create a product revision

        This is very similiar to default "duplicate/copy"-function, but
        it will not generate new default code by sequence, and will
        use the old product name (and won't add (copy) to the end)
        """
        new_product, view_action = self.create_revision()

        # Redirect to new product view
        return view_action

    @api.multi
    def action_create_full_revision(self):
        """
        Create a product revision and update BoMs

        1. Create a new product revision
        2. Search BoMs using the old product
        3. Make new BoM revisions for BoMs using the old product
        4. Create new BoM(s) for new product using the old BoM revision
        """

        old_product_id = self.product_variant_id

        # 1. Create a new product revision
        new_product, view_action = self.create_revision()

        # 2. Search BoMs using the old product in BoM lines
        domain = [("bom_line_ids.product_id", "=", old_product_id.id)]
        matching_boms = self.env["mrp.bom"].search(domain)

        # 3. Make new BoM revisions for BoMs using the old product
        for bom_to_copy in matching_boms:
            bom_vals = {}
            if bom_to_copy.code:
                reference = self.get_next_revision_number(bom_to_copy.code)
                bom_vals = {
                    "code": reference,
                    "product_reference": reference,
                }

            new_bom = self.create_new_bom_revision(bom_to_copy, bom_vals)
            # bom_to_copy.active = False

            # Replace any BoM lines using the old product, with new product
            for new_bom_line in new_bom.bom_line_ids:
                if new_bom_line.product_id == old_product_id:
                    new_bom_line.product_id = new_product.product_variant_id.id

                    new_bom_line.bom_id.message_post(
                        _("Updated line '%s' to '%s'")
                        % (
                            old_product_id.display_name,
                            new_product.product_variant_id.display_name,
                        )
                    )

        # 4. Create new BoM(s) for new product using the old BoM revision
        for bom in self.bom_ids:
            reference = self.get_next_revision_number(bom.code)
            bom_vals = {
                "product_tmpl_id": view_action.get("res_id"),
                "code": reference,
                "product_reference": reference,
            }
            self.create_new_bom_revision(bom, bom_vals)

        # Redirect to new product view
        return view_action

    def create_new_bom_revision(self, bom, values={}):
        """
        Create a new BoM revision
        """
        new_bom = bom.copy(values)
        # bom.active = False

        bom.message_post(body=_("Created a new revision '%s'") % new_bom.display_name)

        new_bom.message_post(
            body=_("Created a new revision from '%s'") % bom.display_name
        )

        return new_bom
