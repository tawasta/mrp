from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    brand = fields.Char(store=True)
    model_year = fields.Char(string="Year Model", store=True)

    workcenter_id = fields.One2many(
        "mrp.workcenter", "maintenance_id", string="Work Center"
    )
    code = fields.Char(string="Machine number")

    dust_removal = fields.Boolean()
    compressed_air = fields.Boolean()
    machine_purpose = fields.Text(string="The purpose of the machine", copy=False)
    location_category_id = fields.Many2one(
        "mrp.workcenter.category", string="Location", copy=False, store=True
    )

    def name_get(self):
        res = []
        for maintenance in self:
            name = f"{maintenance.name} - {maintenance.code}"
            res.append((maintenance.id, name))
        return res

    @api.constrains("location_category_id")
    def _check_location_category_id(self):
        """
        Check if there exists a work center that is connected to this equipment.
        If yes, prevent setting a different Location for this equipment than what
        the connected work center has.
        """
        for record in self:
            if record.location_category_id:
                mismatching_location = self.env["mrp.workcenter"].search(
                    [
                        ("maintenance_id", "=", record.id),
                        ("category_id", "!=", record.location_category_id.id),
                    ]
                )

                if mismatching_location:
                    msg = _(
                        "According to Work Center %(mismatching_location[0].name)s, "
                        "this Equipment's location should be "
                        "%(mismatching_location[0].category_id.name)s."
                    )

                    raise ValidationError(msg)
