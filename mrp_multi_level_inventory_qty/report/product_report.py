from odoo import fields, models, tools


class ProductReport(models.Model):

    _name = "product.report"
    _description = "Product Circulation Report"
    _auto = False

    name = fields.Char("Name", readonly=True)
    date = fields.Datetime("MRP Move Date", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    product_report = fields.Many2one("product.report", readonly=True)
    cost = fields.Float("Cost", readonly=True)
    cost_total = fields.Float("Total cost", readonly=True)
    move_sum = fields.Float("MRP Move Quantity", readonly=True)
    stock_quant = fields.Many2one("stock.quant", "Stock Quant", readonly=True)
    quant_sum = fields.Float("Available Quantity", readonly=True)
    move_quant_sum = fields.Float("Expected Quantity", readonly=True)
    abc_profile_id = fields.Many2one(
        "abc.classification.profile", "ABC Classification Profile", readonly=True
    )
    value = fields.Float("Value", readonly=True)
    sufficiency = fields.Float("Sufficiency", readonly=True)

    def _select_product(self, fields=None, days=1):
        if not fields:
            fields = {}
        # row_number() OVER () AS id, p.id, p.name
        #                (sum(svl.value * currency_table.rate) / NULLIF(sum(
        #                        svl.quantity), 0.0)) * sum(stq.quantity) AS value,
        #                        sum(svl.value * currency_table.rate) / NULLIF(sum(
        #                        svl.quantity * stq.quantity), 0.0)

        select_ = """
                p.id AS id,
                p.id AS product_id,
                ((sum(
                    svl.value * currency_table.rate) / sum(
                        NULLIF(svl.quantity, 0.0))) * stq.quantity) AS value,
                abc_p.id AS abc_profile_id,
                prop.value_float AS cost,
                stq.id AS stock_quant,
                (stq.quantity - stq.reserved_quantity) AS quant_sum,
                sum(mrm.mrp_qty) AS move_sum,
                ((stq.quantity - stq.reserved_quantity) + sum(mrm.mrp_qty)) AS move_quant_sum,

                (
                    (
                        (sum(svl.value * currency_table.rate) / sum(
                        NULLIF(svl.quantity, 0.0))) * stq.quantity
                    )
                        /
                    (
                        NULLIF(((stq.quantity - stq.reserved_quantity
                        + sum(mrm.mrp_qty)) * prop.value_float), 0.0)
                    )
                )
                    * {} AS sufficiency,

                sum(mrm.mrp_qty) * prop.value_float AS cost_total,
                mrm.mrp_date as date,
                t.name AS name
        """.format(
            days
        )

        for field in fields.values():
            select_ += field
        return select_

    def _from_product(self, from_clause="", days=1):
        from_ = """
                product_product p
                    LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                    LEFT JOIN abc_classification_profile abc_p ON (
                        abc_p.id=p.abc_classification_profile_id)
                    LEFT JOIN ir_property prop ON (prop.res_id='product.product,' || p.id)
                    LEFT JOIN product_mrp_area mra ON (mra.product_id=p.id)
                    LEFT JOIN mrp_move mrm ON (
                        mrm.product_mrp_area_id=mra.id AND mrm.mrp_type='d'
                        AND mrm.mrp_date < CURRENT_DATE + INTERVAL '{days} DAY')
                    LEFT JOIN mrp_area m_area ON (m_area.id=mra.mrp_area_id)
                    LEFT JOIN stock_quant stq ON (
                        stq.product_id=p.id AND stq.location_id=m_area.location_id)
                    LEFT JOIN stock_valuation_layer svl ON (svl.product_id=p.id)
                    JOIN {currency_table} ON currency_table.company_id=svl.company_id
                {from_clause}
        """.format(
            days=days,
            currency_table=self.env["res.currency"]._get_query_currency_table(
                {"multi_company": True, "date": {"date_to": fields.Date.today()}}
            ),
            from_clause=from_clause,
        )
        return from_

    def _group_by_product(self, groupby=""):
        groupby_ = """
            t.name,
            abc_profile_id,
            stock_quant,
            date,
            prop.value_float,
            p.id %s
        """ % (
            groupby
        )
        return groupby_

    def _query(
        self,
        with_clause="",
        fields=None,
        groupby="",
        from_clause="",
        days=1,
        category=None,
        product_id=None,
        abc_profile_id=None,
        abc_level_id=None,
    ):

        if not fields:
            fields = {}

        with_ = ("WITH %s" % with_clause) if with_clause else ""

        filters = [category, product_id, abc_profile_id, abc_level_id]
        use_and = ""
        where_clause = ""

        if any(filters):
            where_clause = "WHERE "

        if category:
            use_and = any(filters[-3:]) and " AND " or ""
            where_clause += "t.categ_id = {}{}".format(category, use_and)
        if product_id:
            use_and = any(filters[-2:]) and " AND " or ""
            where_clause += "p.id = {}{}".format(product_id, use_and)
        if abc_level_id:
            use_and = any(filters[-1:]) and " AND " or ""
            where_clause += "p.abc_classification_level_id = {}{}".format(
                abc_level_id, use_and
            )
        if abc_profile_id:
            where_clause += "p.abc_classification_profile_id = {}".format(
                abc_profile_id
            )

        return "%s SELECT %s FROM %s%s GROUP BY %s" % (
            with_,
            self._select_product(fields, days=days),
            self._from_product(from_clause, days=days),
            where_clause,
            self._group_by_product(groupby),
        )

    def init(self):
        days = self.env.context.get("number_of_days", 1)
        category = self.env.context.get("product_category_id", None)
        product_id = self.env.context.get("product_id", None)
        abc_profile_id = self.env.context.get("abc_profile_id", None)
        abc_level_id = self.env.context.get("abc_level_id", None)
        # self._table = product_report
        tools.drop_view_if_exists(self._cr, self._table)
        #        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s);"""
            % (
                self._table,
                self._query(
                    days=days,
                    category=category,
                    product_id=product_id,
                    abc_profile_id=abc_profile_id,
                    abc_level_id=abc_level_id,
                ),
            )
        )
