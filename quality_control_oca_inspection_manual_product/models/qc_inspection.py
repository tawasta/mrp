from odoo import api, fields, models
from odoo.exceptions import ValidationError


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=False,
        tracking=True,
        help="Product that was inspected. Prefilled from the reference "
        "(product, stock move or lot); can be set by hand when the reference "
        "is something else (e.g. a sale order), and may be left empty.",
    )

    def _reference_product_id(self):
        """Product that ``object_id`` itself identifies, if any.

        ``product_id`` is locked to this value; it can only be entered by hand
        when this returns an empty recordset.
        """
        self.ensure_one()
        obj = self.object_id
        if obj and obj._name == "product.product":
            return obj
        if obj and obj._name in ("stock.move", "stock.lot"):
            return obj.product_id
        return self.env["product.product"]

    def _compute_product_id(self):
        # Base + stock glue blank product_id whenever object_id has no product
        # to give; keep a value that was entered by hand instead.
        manual = {i.id: i.product_id for i in self if i.product_id}
        res = super()._compute_product_id()
        for inspection in self:
            if not inspection.product_id and inspection.id in manual:
                inspection.product_id = manual[inspection.id]
        return res

    @api.constrains("product_id", "object_id")
    def _check_product_id_matches_reference(self):
        for inspection in self:
            reference_product = inspection._reference_product_id()
            if reference_product and inspection.product_id != reference_product:
                raise ValidationError(
                    self.env._(
                        "The inspected product is taken automatically from the "
                        "reference (%(ref)s) and cannot be changed by hand. "
                        "Manual entry is only possible when the reference does "
                        "not identify a product.",
                        ref=inspection.object_id.display_name,
                    )
                )
