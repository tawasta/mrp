from odoo import fields, models


class MrpWorkcenter(models.Model):

    _inherit = "mrp.workcenter"

    energy_consumption = fields.Float(string="Energy per hour (active)")
    energy_consumption_passive = fields.Float(string="Energy per hour (passive)")
    bom_consu = fields.Many2one(
        "mrp.bom", string="Consumable BOM", domain=[("type", "=", "consumption")]
    )
    category_id = fields.Many2one("mrp.workcenter.category", string="Category")
    maintenance_id = fields.Many2one(
        "maintenance.equipment", string="Machine", copy=False
    )
    checked = fields.Boolean(
        string="Measured",
        copy=False,
        help="If the enery consumption has been measured.",
    )
