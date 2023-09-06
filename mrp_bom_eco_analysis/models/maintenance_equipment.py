from odoo import fields, models


class MaintenanceEquipment(models.Model):

    _inherit = "maintenance.equipment"

    brand = fields.Char(string="Brand", store=True)
    model_year = fields.Char(string="Year Model", store=True)

    workcenter_id = fields.One2many(
        "mrp.workcenter", "maintenance_id", string="Work Center"
    )
    code = fields.Char(string="Machine number")

    dust_removal = fields.Boolean(string="Dust removal")
    compressed_air = fields.Boolean(string="Compressed Air")
    machine_purpose = fields.Text(string="The purpose of the machine", copy=False)
    # location is only an informational field. It works the same in Odoo 16 version.
    # So changing its type is not dangerous. Though changing a field type is not
    # advisable.
    location = fields.Many2one("mrp.workcenter.category")

    def name_get(self):
        res = []
        for maintenance in self:
            name = "{} - {}".format(maintenance.name, maintenance.code)
            res.append((maintenance.id, name))
        return res
