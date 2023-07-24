from odoo import fields, models


class MrpWorkcenter(models.Model):

    _inherit = "mrp.workcenter"

    energy_consumption = fields.Float(string="Energy per hour (active)")
    energy_consumption_passive = fields.Float(string="Energy per hour (passive)")
    bom_consu = fields.Many2one(
        "mrp.bom", string="Consumable BOM", domain=[("type", "=", "consumption")]
    )
    category_id = fields.Many2one("mrp.workcenter.category", string="Location")
    maintenance_id = fields.Many2one(
        "maintenance.equipment", string="Machine", copy=False
    )
    checked = fields.Date(
        string="Measured",
        copy=False,
        help="When the energy consumption has been measured.",
    )

    work_type = fields.Char(string="Work type", copy=False)
    electric_consumption = fields.Float(string="Electric consumption", copy=False)
    workcenter_lower_exist = fields.Boolean(
        compute=lambda self: self._compute_workcenter_lower_id()
    )

    workcenter_upper_id = fields.Many2one(
        "mrp.workcenter",
        string="Workcenter upper",
        domain="[('id', '!=', id), ('id', 'not in', workcenter_lower_id)]",
    )
    workcenter_lower_id = fields.One2many(
        "mrp.workcenter", "workcenter_upper_id", string="Workcenter lower"
    )

    def _compute_workcenter_lower_id(self):
        for center in self:
            if center.workcenter_lower_id:
                center.workcenter_lower_exist = True
            else:
                center.workcenter_lower_exist = False
