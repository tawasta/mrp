from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    location = fields.Many2one(
        "mrp.workcenter.category", deprecated=True, string="Old location field"
    )
    location_category_id = fields.Many2one(
        "mrp.workcenter.category", string="Location", copy=False, store=True
    )

    def name_get(self):
        res = []
        for maintenance in self:
            name = "{} - {}".format(maintenance.name, maintenance.code)
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
                work_centers_with_mismatching_location = self.env[
                    "mrp.workcenter"
                ].search(
                    [
                        ("maintenance_id", "=", record.id),
                        ("category_id", "!=", record.location_category_id.id),
                    ]
                )

                if work_centers_with_mismatching_location:
                    msg = _(
                        "According to Work Center {}, this Equipment's location "
                        "should be {}."
                    ).format(
                        work_centers_with_mismatching_location[0].name,
                        work_centers_with_mismatching_location[0].category_id.name,
                    )

                    raise ValidationError(msg)
