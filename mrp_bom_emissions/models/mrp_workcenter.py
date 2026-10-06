from odoo import fields, models


class MrpWorkcenter(models.Model):
    _name = "mrp.workcenter"
    _inherit = ["mrp.workcenter"]

    co2_emissions_per_time_unit = fields.Float()
    co2_emissions_per_production_unit = fields.Float()
