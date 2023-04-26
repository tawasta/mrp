from odoo import fields, models


class MrpWorkcenter(models.Model):

    _inherit = "mrp.workcenter"

    energy_consumption = fields.Float(string="Energy per hour")
    bom_consu = fields.Many2one(
        "mrp.bom", string="Consumable BOM", domain=[("type", "=", "consumption")]
    )
    category_id = fields.Many2one("mrp.workcenter.category", string="Category")


#    maintenance_id
