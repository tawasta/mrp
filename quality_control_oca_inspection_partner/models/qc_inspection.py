from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        compute="_compute_partner_id",
        store=True,
        readonly=False,
        tracking=True,
        help="Partner this inspection concerns. Prefilled from the referenced "
        "document; can be set manually.",
    )

    def _object_partner_field_names(self):
        """Field names probed, in order, on the referenced record to derive the
        partner. Override to support extra object types."""
        return ["partner_id", "commercial_partner_id"]

    def _get_object_partner(self):
        """``res.partner`` recordset derived from ``object_id`` (empty if none).

        Overridable hook for object types the field-name heuristic does not
        cover (e.g. walking ``stock.move.picking_id.partner_id``).
        """
        self.ensure_one()
        obj = self.object_id
        if not obj:
            return self.env["res.partner"]
        if obj._name == "res.partner":
            return obj[:1]
        for fname in self._object_partner_field_names():
            if fname in obj._fields and obj[fname]:
                return obj[fname][:1]
        return self.env["res.partner"]

    @api.depends("object_id")
    def _compute_partner_id(self):
        for inspection in self:
            partner = inspection._get_object_partner()
            if partner:
                inspection.partner_id = partner
            elif not inspection.partner_id:
                inspection.partner_id = False
