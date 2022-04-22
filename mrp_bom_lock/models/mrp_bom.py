from odoo import api, models


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    def is_locked(self, bom):
        """ Checks if given BOM or any of it's parent BOM's have
            their bom locked.
            Returns tuple with locked boolean and locked template record.
            This can be called from anywhere with a BOM record
        """

        if bom.product_tmpl_id.bom_locked:
            return True, bom.product_tmpl_id

        line_obj = self.env["mrp.bom.line"]
        # gets product ids from current product template
        product_ids = [x.id for x in bom.product_tmpl_id.product_variant_ids]
        # searches for any bom lines with product ids.
        line_ids = line_obj.search([("product_id", "in", product_ids)])
        # checks all parent boms recursively.
        parent_boms = [x.bom_id for x in line_ids]
        if parent_boms:
            for parent in parent_boms:
                res = self.is_locked(parent)
                if res[0]:
                    return res

        return False, []

    def locked_message(self, template):
        return "BOM is locked for product: %s" % template.display_name

    def display_locked_message(self, template):
        message = self.locked_message(template)
        raise Warning(message)

    def bom_lock_rules(self):
        return self.env.user.has_group("mrp_bom_lock.bom_lock_allow_write")

    @api.multi
    def write(self, values):
        """ Write triggers is_locked check for current BOM"""
        if not self.bom_lock_rules():
            for bom in self:
                res = self.is_locked(bom)
                if res[0]:
                    self.display_locked_message(res[1])

        return super(MrpBom, self).write(values)
