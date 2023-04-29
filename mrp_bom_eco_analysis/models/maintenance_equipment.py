from odoo import fields, models


class MaintenanceEquipment(models.Model):

    _inherit = "maintenance.equipment"

    brand = fields.Char(string="Brand", store=True)
    model_year = fields.Char(string="Year Model", store=True)
