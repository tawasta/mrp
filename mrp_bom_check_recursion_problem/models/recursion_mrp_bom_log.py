from odoo import fields, models


class RecursionMrpBomLog(models.Model):
    _name = "recursion.mrp.bom.log"
    _description = "Recursion MRP BoM"

    name = fields.Text()
    problem_products = fields.Text()
