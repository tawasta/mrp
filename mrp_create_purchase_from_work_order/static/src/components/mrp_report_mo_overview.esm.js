/** @odoo-module **/

import {MoOverviewLine} from "@mrp/components/mo_overview_line/mrp_mo_overview_line";
import {MoOverviewOperationsBlock} from "@mrp/components/mo_overview_operations_block/mrp_mo_overview_operations_block";

MoOverviewOperationsBlock.props.summary.shape.sub_uom_name = {
    type: String,
    optional: true,
};
MoOverviewLine.props.data.shape.sub_uom_name = {type: String, optional: true};
