from odoo import fields, models, tools


class ProductReport(models.Model):

    _name = "product.report"
    _description = "Product Circulation Report"
    _auto = False

    name = fields.Char("Name", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    cost = fields.Float("Cost", readonly=True)
    cost_total = fields.Float("Total cost", readonly=True)
    move_sum = fields.Float("Move sum", readonly=True)

    def _select_product(self, fields=None):
        if not fields:
            fields = {}

        #            row_number() OVER () AS id, p.id, p.name
        #                CASE WHEN mrm IS NOT NULL THEN sum(mrm.mrp_qty) ELSE 0 END as move_sum,
        select_ = """
                p.id as id,
                p.id as product_id,
                prop.value_float as cost,
                sum(mrm.mrp_qty) as move_sum,
                sum(mrm.mrp_qty) * prop.value_float as cost_total,
                t.name as name
        """

        for field in fields.values():
            select_ += field
        return select_

    def _from_product(self, from_clause=""):
        from_ = (
            """
                product_product p
                    left join product_template t on (p.product_tmpl_id=t.id)
                    left join ir_property prop on (prop.res_id='product.product,' || p.id)
                    left join product_mrp_area mra on (mra.product_id=p.id)
                    left join mrp_move mrm on (mrm.product_mrp_area_id=mra.id)
                    JOIN (SELECT SUM(mrp_qty) as move_sum FROM mrm) all_mrm_qty
                %s
        """
            % from_clause
        )
        return from_

    def _group_by_product(self, groupby=""):
        groupby_ = """
            t.name,
            mrm.mrp_qty,
            prop.value_float,
            mrm,
            p.id %s
        """ % (
            groupby
        )
        return groupby_

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if not fields:
            fields = {}
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        return "%s (SELECT %s FROM %s GROUP BY %s)" % (
            with_,
            self._select_product(fields),
            self._from_product(from_clause),
            self._group_by_product(groupby),
        )

    def init(self):
        # self._table = product_report
        tools.drop_view_if_exists(self._cr, self._table)
        #        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query())
        )
