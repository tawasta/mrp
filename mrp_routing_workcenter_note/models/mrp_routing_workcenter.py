from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    # Removed from core in 19.0. Recreated with the same name and type as in
    # 17.0 so that the existing descriptions and their translations are kept.
    note = fields.Html("Description", translate=True)
