import logging
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, _, api, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare

from odoo.addons.mrp.models.stock_rule import (
    StockRule as MrpStockRule,
)
from odoo.addons.stock.models.stock_rule import ProcurementException, ProcurementGroup

_logger = logging.getLogger(__name__)


# ruff: noqa: E501
# ruff: noqa: E402
def _make_mo_get_domain(self, procurement, bom):
    gpo = self.group_propagation_option
    group = (
        (gpo == "fixed" and self.group_id)
        or (
            gpo == "propagate"
            and "group_id" in procurement.values
            and procurement.values["group_id"]
        )
        or False
    )
    domain = (
        ("bom_id", "=", bom.id),
        ("product_id", "=", procurement.product_id.id),
        ("state", "in", ["draft", "confirmed"]),
        ("is_planned", "=", False),
        ("picking_type_id", "=", self.picking_type_id.id),
        ("company_id", "=", procurement.company_id.id),
        ("user_id", "=", False),
        ("location_dest_id", "child_of", procurement.location_id.id),
    )
    if procurement.values.get("orderpoint_id"):
        procurement_date = datetime.combine(
            fields.Date.to_date(procurement.values["date_planned"])
            - relativedelta(days=int(bom.produce_delay)),
            datetime.max.time(),
        )
        domain += (
            "|",
            "&",
            ("state", "=", "draft"),
            ("date_deadline", "<=", procurement_date),
            "&",
            ("state", "=", "confirmed"),
            ("date_start", "<=", procurement_date),
        )
    if group:
        domain += (("procurement_group_id", "=", group.id),)
    return domain


# ruff: noqa: E501
# ruff: noqa: E402
@api.model
def _run_manufacture(self, procurements):
    new_productions_values_by_company = defaultdict(list)
    _logger.info(
        f"RUN MANUFACTURE NEW PRODUCTIONS VALUES: {new_productions_values_by_company}"
    )
    for procurement, rule in procurements:
        _logger.info(f"RUN MANUFACTURE PROCUREMENT: {procurement}")
        _logger.info(f"RUN MANUFACTURE RULE: {rule}")
        if (
            float_compare(
                procurement.product_qty,
                0,
                precision_rounding=procurement.product_uom.rounding,
            )
            <= 0
        ):
            # If procurement contains negative quantity, don't create a MO that would be for a negative value.
            continue
        bom = rule._get_matching_bom(
            procurement.product_id, procurement.company_id, procurement.values
        )

        _logger.info(f"RUN MANUFACTURE BOM: {bom}")
        _logger.info(f"RUN MANUFACTURE RULE: {rule}")

        mo = self.env["mrp.production"]
        mto_route = self.env["stock.warehouse"]._find_global_route(
            "stock.route_warehouse0_mto", _("Replenish on Order (MTO)")
        )
        if rule.route_id != mto_route and procurement.origin != "MPS":
            domain = _make_mo_get_domain(rule, procurement, bom)
            _logger.info(f"RUN MANUFACTURE DOMAIN: {domain}")
            mo = self.env["mrp.production"].sudo().search(domain, limit=1)
        if not mo:
            new_productions_values_by_company[procurement.company_id.id].append(
                rule._prepare_mo_vals(*procurement, bom)
            )
            _logger.info("RUN MANUFACTURE NOT MO")
        else:
            _logger.info("RUN MANUFACTURE CHANGE QTY")
            self.env["change.production.qty"].sudo().with_context(
                skip_activity=True
            ).create(
                {
                    "mo_id": mo.id,
                    "product_qty": mo.product_id.uom_id._compute_quantity(
                        (mo.product_uom_qty + procurement.product_qty),
                        mo.product_uom_id,
                    ),
                }
            ).change_prod_qty()

    note_subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note")
    for company_id, productions_values in new_productions_values_by_company.items():
        # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        productions = (
            self.env["mrp.production"]
            .with_user(SUPERUSER_ID)
            .sudo()
            .with_company(company_id)
            .create(productions_values)
        )
        _logger.info(f"RUN PRODUCTIONS: {productions}")
        productions.filtered(self._should_auto_confirm_procurement_mo).action_confirm()

        for production in productions:
            origin_production = (
                production.move_dest_ids
                and production.move_dest_ids[0].raw_material_production_id
                or False
            )
            orderpoint = production.orderpoint_id
            if (
                orderpoint
                and orderpoint.create_uid.id == SUPERUSER_ID
                and orderpoint.trigger == "manual"
            ):
                production.message_post(
                    body=_(
                        "This production order has been created from Replenishment Report."
                    ),
                    message_type="comment",
                    subtype_id=note_subtype_id,
                )
            elif orderpoint:
                production.message_post_with_source(
                    "mail.message_origin_link",
                    render_values={"self": production, "origin": orderpoint},
                    subtype_id=note_subtype_id,
                )
            elif origin_production:
                production.message_post_with_source(
                    "mail.message_origin_link",
                    render_values={"self": production, "origin": origin_production},
                    subtype_id=note_subtype_id,
                )
    return True


MrpStockRule._run_manufacture = _run_manufacture


# ruff: noqa: E501
# ruff: noqa: E402
# ruff: noqa: B905
# pylint: disable=W8120
@api.model
def run(self, procurements, raise_user_error=True):
    """Fulfil `procurements` with the help of stock rules.

    Procurements are needs of products at a certain location. To fulfil
    these needs, we need to create some sort of documents (`stock.move`
    by default, but extensions of `_run_` methods allow to create every
    type of documents).

    :param procurements: the description of the procurement
    :type list: list of `~odoo.addons.stock.models.stock_rule.ProcurementGroup.Procurement`
    :param raise_user_error: will raise either an UserError or a ProcurementException
    :type raise_user_error: boolan, optional
    :raises UserError: if `raise_user_error` is True and a procurement isn't fulfillable
    :raises ProcurementException: if `raise_user_error` is False and a procurement isn't fulfillable
    """

    def raise_exception(procurement_errors):
        if raise_user_error:
            dummy, errors = zip(*procurement_errors)
            raise UserError("\n".join(errors))
        else:
            raise ProcurementException(procurement_errors)

    actions_to_run = defaultdict(list)
    procurement_errors = []
    for procurement in procurements:
        procurement.values.setdefault("company_id", procurement.location_id.company_id)
        procurement.values.setdefault("priority", "0")
        procurement.values.setdefault(
            "date_planned",
            procurement.values.get("date_planned", False) or fields.Datetime.now(),
        )
        if self._skip_procurement(procurement):
            continue
        rule = self._get_rule(
            procurement.product_id, procurement.location_id, procurement.values
        )
        _logger.info(f"RUN RULE: {rule}")
        if not rule:
            error = _(
                "No rule has been found to replenish %r in %r.\nVerify the routes configuration on the product.",
                procurement.product_id.display_name,
                procurement.location_id.display_name,
            )
            procurement_errors.append((procurement, error))
        else:
            action = "pull" if rule.action == "pull_push" else rule.action
            actions_to_run[action].append((procurement, rule))

    if procurement_errors:
        raise_exception(procurement_errors)

    _logger.info(f"RUN ACTIONS TO RUN: {actions_to_run}")

    for action, procurements in actions_to_run.items():
        _logger.info(f"RUN ACTION: {action}")
        _logger.info(f"RUN ACTION PROCUREMENT: {procurements}")
        if hasattr(self.env["stock.rule"], "_run_%s" % action):
            try:
                getattr(self.env["stock.rule"], "_run_%s" % action)(procurements)
            except ProcurementException as e:
                procurement_errors += e.procurement_exceptions
        else:
            _logger.error(
                "The method _run_%s doesn't exist on the procurement rules" % action
            )

    if procurement_errors:
        raise_exception(procurement_errors)
    return True


ProcurementGroup.run = run
