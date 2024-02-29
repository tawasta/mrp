from odoo import api, fields, models, tools


class ProductReport(models.Model):

    _name = "product.report"
    _description = "Product Circulation Report"
    _auto = False

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        """Changed how column sums work"""
        res = super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        if "sufficiency:sum" in fields and len(res) == 1:
            if (
                res
                and res[0].get("year_sufficiency")
                and res[0].get("total_year_sufficiency")
            ):
                res[0]["year_sufficiency"] = res[0]["total_year_sufficiency"]
            if res and res[0].get("sufficiency") and res[0].get("total_sufficiency"):
                res[0]["sufficiency"] = res[0]["total_sufficiency"]

        return res

    name = fields.Char("Name", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    cost = fields.Float("Cost", readonly=True)
    cost_total = fields.Float("Demand Value", readonly=True)
    move_sum = fields.Float("Demand Quantity", readonly=True)
    stock_quant = fields.Many2one("stock.quant", "Stock Quant", readonly=True)
    quant_sum = fields.Float("Quantity Now", readonly=True)
    abc_profile_id = fields.Many2one(
        "abc.classification.profile", "ABC Classification Profile", readonly=True
    )
    value = fields.Float("Value now", readonly=True)
    sufficiency = fields.Float("Coverage in Days", readonly=True)
    year_sufficiency = fields.Float("Inventory Turnover", readonly=True)
    total_year_sufficiency = fields.Float("Total Inventory Turnover", readonly=True)
    total_sufficiency = fields.Float("Total Coverage in Days", readonly=True)
    temp_value = fields.Float("Temp Value", readonly=True)
    temp_qty = fields.Float("Temp Qty", readonly=True)
    temp_float = fields.Float("Temp Float", readonly=True)

    def _select_product(self, fields=None, days=1):
        if not fields:
            fields = {}

        select_ = """
                p.id AS id,
                p.id AS product_id,

                min(temp_value.value) AS temp_value,
                min(temp_float.value_float) AS temp_float,

                (min(temp_value.value) / NULLIF(
                    min(temp_float.value_float), 0.0)) * {} AS total_sufficiency,

                365 / NULLIF(((min(temp_value.value) /
                    NULLIF(min(temp_float.value_float), 0.0)) * {}), 0.0)
                        AS total_year_sufficiency,

                (SELECT sum(value) FROM stock_valuation_layer
                    WHERE product_id = p.id) AS value,
                abc_p.id AS abc_profile_id,
                prop.value_float AS cost,
                stq.id AS stock_quant,
                (SELECT sum(quantity) FROM stock_valuation_layer
                    WHERE product_id = p.id) AS quant_sum,
                sum(mrm.mrp_qty) * -1 AS move_sum,

                (
                    (
                        (SELECT sum(value) FROM stock_valuation_layer WHERE product_id = p.id)
                    )
                        /
                    (
                        NULLIF((SUM(mrm.mrp_qty) * -1 * prop.value_float), 0.0)
                    )
                )
                    * {} AS sufficiency,

                365 / NULLIF(((
                    (
                        (SELECT sum(value) FROM stock_valuation_layer WHERE product_id = p.id)
                    )
                        /
                    (
                        NULLIF((SUM(mrm.mrp_qty) * -1 * prop.value_float), 0.0)
                    )
                )
                    * {}), 0.0) AS year_sufficiency,

                sum(mrm.mrp_qty) * -1 * prop.value_float AS cost_total,

                t.name AS name
        """.format(
            days, days, days, days
        )

        for field in fields.values():
            select_ += field
        return select_

    def _from_product(self, from_clause="", days=1):
        from_ = """
                temp_value, temp_float, product_product p
                    LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                    LEFT JOIN abc_classification_profile abc_p ON (
                        abc_p.id=p.abc_classification_profile_id)
                    LEFT JOIN ir_property prop ON (prop.res_id='product.product,' || p.id)
                    LEFT JOIN product_mrp_area mra ON (mra.product_id=p.id)
                    LEFT JOIN mrp_move mrm ON (
                        mrm.product_id=p.id AND mrm.mrp_type='d'
                        AND mrm.mrp_date < CURRENT_DATE + INTERVAL '{days} DAY')
                    LEFT JOIN mrp_area m_area ON (m_area.id=mra.mrp_area_id)
                    LEFT JOIN stock_quant stq ON (
                        stq.product_id=p.id AND stq.location_id=m_area.location_id)
                    LEFT JOIN {currency_table} ON currency_table.company_id=stq.company_id
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
        abc_level_ids=None,
    ):

        if not fields:
            fields = {}

        def variant_generator(category):
            products = self.env["product.product"].search([])
            for product in products:
                if product.product_tmpl_id.categ_id.id == category:
                    yield product.id

        where_clause = ""
        search_domain = []
        variants = []

        if category:
            variants = list(variant_generator(category))
        if product_id:
            search_domain += [("id", "=", product_id)]
        if abc_level_ids:
            search_domain += [("abc_classification_level_id", "in", abc_level_ids)]
        if abc_profile_id:
            search_domain += [("abc_classification_profile_id", "=", abc_profile_id)]

        if search_domain:
            product_ids = (
                self.env["product.product"].search(search_domain).ids + variants
            )
        elif variants:
            product_ids = variants
        else:
            product_ids = self.env["product.product"].search([]).ids

        # We avoid an error for "product_id IN (37337,)" in WHERE statement
        # with this trick.
        if len(product_ids) == 1:
            product_ids = tuple(product_ids + product_ids)
        else:
            product_ids = tuple(product_ids)

        if not product_ids:
            product_ids = "(NULL, NULL)"

        with_clause = """
                temp_value (value) AS
                    (SELECT sum(value) FROM stock_valuation_layer WHERE product_id IN {}),
                temp_float (value_float) AS
                    (SELECT sum(temp_mrm.mrp_qty * -1 * temp_prop.value_float)
                    FROM product_product temp_p
                        LEFT JOIN mrp_move temp_mrm ON (
                            temp_mrm.product_id=temp_p.id AND temp_mrm.mrp_type='d'
                            AND temp_mrm.mrp_date < CURRENT_DATE + INTERVAL '{} DAY')
                        LEFT JOIN ir_property temp_prop
                            ON (temp_prop.res_id='product.product,' || temp_p.id)
                    WHERE temp_p.id IN {})
            """.format(
            product_ids,
            days,
            product_ids,
        )

        with_ = ("WITH %s" % with_clause) if with_clause else ""

        where_clause = "WHERE p.id in {} AND t.purchase_ok".format(product_ids)

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
        abc_level_ids = self.env.context.get("abc_level_ids", None)
        tools.drop_view_if_exists(self._cr, "product_report")
        self.env.cr.execute(
            """CREATE or REPLACE VIEW product_report as (%s);"""
            % (
                self._query(
                    days=days,
                    category=category,
                    product_id=product_id,
                    abc_profile_id=abc_profile_id,
                    abc_level_ids=abc_level_ids,
                )
            )
        )
