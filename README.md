[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Pipeline Status](https://gitlab.com/tawasta/odoo/mrp/badges/14.0-dev/pipeline.svg)](https://gitlab.com/tawasta/odoo/mrp/-/pipelines/)

MRP
====
MRP Addons for Odoo.

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[bsm_importer](bsm_importer/) | 14.0.1.0.0 |  | Import data from local file system to database
[material_requirement_planning](material_requirement_planning/) | 14.0.1.0.1 |  | Material Requirement
[mrp_auditlog_rules](mrp_auditlog_rules/) | 14.0.1.0.0 |  | Adds audit log rules for mrp.bom
[mrp_bom_component_change_wizard](mrp_bom_component_change_wizard/) | 14.0.1.0.1 |  | MRP BoM component change wizard
[mrp_bom_cost_control_log](mrp_bom_cost_control_log/) | 14.0.1.1.0 |  | Adds log lines for products which are produced from BoM cost computations
[mrp_bom_cost_cron](mrp_bom_cost_cron/) | 14.0.1.0.3 |  | Cron for MRP compute cost
[mrp_bom_eco_analysis](mrp_bom_eco_analysis/) | 14.0.1.1.16 |  | ECO analysis modifications
[mrp_bom_limit_increase](mrp_bom_limit_increase/) | 14.0.1.0.0 |  | Incrases BOM tree-view limit to 100
[mrp_bom_operation_template](mrp_bom_operation_template/) | 14.0.1.0.2 |  | Templates for different operations
[mrp_bom_structure_xlsx_cost](mrp_bom_structure_xlsx_cost/) | 14.0.1.0.0 |  | Add cost to MRP BOM Structure XLSX
[mrp_bom_structure_xlsx_recursive](mrp_bom_structure_xlsx_recursive/) | 14.0.2.15.38 |  | Export an excel for LCA report of a BoM
[mrp_default_focus](mrp_default_focus/) | 14.0.1.0.0 |  | Sets default focus fields for MRP
[mrp_excel_bom_import_flat](mrp_excel_bom_import_flat/) | 14.0.1.0.1 |  | Import template for importing a flat Bill of Material
[mrp_inventory_hide_forecasted_inventory](mrp_inventory_hide_forecasted_inventory/) | 14.0.1.0.0 |  | Hide Forecasted Inventory in MRP Inventory tree view
[mrp_inventory_hide_mrp_area](mrp_inventory_hide_mrp_area/) | 14.0.1.0.0 |  | Hide MRP Area in MRP Inventory tree view
[mrp_inventory_product_category](mrp_inventory_product_category/) | 14.0.1.0.0 |  | Shows product category in mrp.inventory list view
[mrp_inventory_responsible_id](mrp_inventory_responsible_id/) | 14.0.1.0.0 |  | Shows product template responsible id in mrp.inventory list view
[mrp_inventory_sh_product_tags_filter](mrp_inventory_sh_product_tags_filter/) | 14.0.1.0.0 |  | MRP Inventory - Group and Filter by SH product tags
[mrp_inventory_supplier_info](mrp_inventory_supplier_info/) | 14.0.1.0.0 |  | Shows supplier info from mrp area in mrp inventory views
[mrp_inventory_tree_reorder_running_availability](mrp_inventory_tree_reorder_running_availability/) | 14.0.1.0.0 |  | Reorder Running Availability in MRP Inventory tree
[mrp_kit_compulsory_components](mrp_kit_compulsory_components/) | 14.0.1.0.0 |  | Components are compulsory if created BOM is a kit
[mrp_move_current_date_to_scheduled_date](mrp_move_current_date_to_scheduled_date/) | 14.0.1.0.0 |  | MRP Move Current Date To Scheduled Date
[mrp_move_hide_current_qty](mrp_move_hide_current_qty/) | 14.0.1.0.0 |  | Hide current_qty on Mrp Move
[mrp_move_hide_parent_product_id](mrp_move_hide_parent_product_id/) | 14.0.1.0.0 |  | Hide parent_product_id on Mrp Move
[mrp_move_hide_planned_order_up_ids](mrp_move_hide_planned_order_up_ids/) | 14.0.1.0.0 |  | Hide planned_order_up_ids on Mrp Move
[mrp_move_vendor](mrp_move_vendor/) | 14.0.1.0.0 |  | Show Vendor on MRP Moves
[mrp_multi_level_area_form_group](mrp_multi_level_area_form_group/) | 14.0.1.0.0 |  | Manufacture / User group enables to see MRP Moves
[mrp_multi_level_create_parameter_from_so](mrp_multi_level_create_parameter_from_so/) | 14.0.1.0.0 |  | Product Area parameter is created after SO confirmation
[mrp_multi_level_create_parameter_from_so_bom_recursive](mrp_multi_level_create_parameter_from_so_bom_recursive/) | 14.0.1.0.3 |  | Sale order line product BoM is run through recursively
[mrp_multi_level_inventory_qty](mrp_multi_level_inventory_qty/) | 14.0.1.1.16 |  | Inventory product circulation report
[mrp_multi_level_move_forecasted_qty](mrp_multi_level_move_forecasted_qty/) | 14.0.1.0.0 |  | Forecasted quantity for mrp.move
[mrp_multi_level_optimization](mrp_multi_level_optimization/) | 14.0.1.0.0 |  | MRP multi level optimization
[mrp_multi_level_parameter_abc](mrp_multi_level_parameter_abc/) | 14.0.1.1.0 |  | MRP product parameter ABC Fields
[mrp_multi_level_queue](mrp_multi_level_queue/) | 14.0.1.0.0 |  | MRP Multi Level with queue jobs
[mrp_operations_disable_sequence_dragging](mrp_operations_disable_sequence_dragging/) | 14.0.1.0.0 |  | Hides sequence column in operations tree view
[mrp_product_only_select](mrp_product_only_select/) | 14.0.1.0.0 |  | Disable creating and editing of products from the MO product field
[mrp_production_autoprocess_work_orders](mrp_production_autoprocess_work_orders/) | 14.0.1.0.3 |  | Created Work Orders get completed instantly
[mrp_production_autoprocess_work_orders_two_steps](mrp_production_autoprocess_work_orders_two_steps/) | 14.0.1.0.0 |  | Created Work Orders get completed in two steps
[mrp_production_mass_cancel](mrp_production_mass_cancel/) | 14.0.1.0.0 |  | Allow cancellation of production orders en masse
[mrp_production_set_bom_regardless_of_operation_type](mrp_production_set_bom_regardless_of_operation_type/) | 14.0.1.0.0 |  | Set BoM that is not based on Operation Type
[mrp_production_tree_date_planned_start_as_date](mrp_production_tree_date_planned_start_as_date/) | 14.0.1.0.0 |  | Show date planned start as date in mrp production tree
[mrp_report_bom_structure_product_unit_price](mrp_report_bom_structure_product_unit_price/) | 14.0.1.0.0 |  | Use product Unit price instead of its multiple on report
[mrp_unbuild_note_for_mo](mrp_unbuild_note_for_mo/) | 14.0.1.0.0 |  | Unbuild note to Manufacturing order
[product_bom_relation_purchased_and_sold_info](product_bom_relation_purchased_and_sold_info/) | 14.0.1.0.0 |  | Purchased and Sold Product Quantities in BOM tree view
[product_bom_relation_quantity_count](product_bom_relation_quantity_count/) | 14.0.1.0.0 |  | Used Product Quantities in BOM tree view
[product_mrp_area_mrp_profile_header](product_mrp_area_mrp_profile_header/) | 14.0.1.0.0 |  | Adds header "MRP Profile" to MRP Area form
[product_mrp_area_show_qty_available](product_mrp_area_show_qty_available/) | 14.0.1.0.0 |  | Show qty_available on Product Mrp Area

[//]: # (end addons)
