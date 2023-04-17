from odoo import fields, models


class MrpWorkcenterCategory(models.Model):

    _name = "mrp.workcenter.category"
    _description = "Mrp Workcenter Category"

    name = fields.Char(string="Name")
