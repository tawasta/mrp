from odoo import fields, models


class MaintenanceEquipment(models.Model):

    _inherit = "maintenance.equipment"

    brand = fields.Char(string="Brand", store=True)
