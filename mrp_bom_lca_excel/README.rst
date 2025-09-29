.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
LCA report of a bill of materials
=================================

LCA means Life Cycle Analysis. This kind of analysis seeks to inspect
environmental impacts of a product. So energy and material consumptions
are needed to be calculated. This module creates an excel to calculate
those values from a bill of materials.


Report creates 5 sheets to an excel:

1. BOM materials, which lists these to an excel:

    - Internal category/display name
    - Level
    - Internal reference
    - Name
    - Unit
    - Quantity in products
    - Part name
    - Material
    - Material class
    - Material weight / per unit
    - Material total weight in product
    - Weight unit
    - Recycle material %
    - Waste products
    - Waste endpoint
    - Vendor
    - Vendor Address
    - Supply Address
    - Country of origin

2. BOM by-products, which lists:

    - Internal category/display name
    - Level
    - Product to which operation is done
    - Product internal reference
    - Operation ID
    - Operation name
    - Waste product name
    - Waste amount
    - Waste unit

3. Operations, energy, consumption:

    - Internal category/display name
    - Product internal reference
    - Name
    - Operation ID
    - Operation name
    - Energy consumption during an operation / Total(kWh)
    - Energy Unit
    - Operation consumptions product ID
    - Name of the product consumed in an operation
    - Consumed amount / produced 1 product
    - Unit

4. Product requirements:

    - Internal category/display name
    - Level
    - Product internal reference
    - Name
    - Unit
    - Part name
    - Material
    - Material class
    - Net weight in a product
    - Net weight Unit
    - Dangerous materials
    - RoHS
    - REACH
    - SCIP
    - POP (Persistant Organic Pollutants
    - Halogens
    - Conflict Area Minerals
    - Recycle material %
    - Waste product
    - Waste endpoint

5. Material summaries, which has the summaries of materials and energy consumption:
    - 1. Product Materials Summary
    - 2. Packaging Materials Summary
    - 3. Product component materials
    - 4. Delivery Packaging materials
    - 5. All materials consumed in production
    - 6. All materials in Incoming packaging
    - 7. Summary of all materials
    - 8. Workcenters Energy summary
    - 9. Operations Energy summary

Configuration
=============
These sheets can be hidden from Manufacturing settings:
- BOM by-products
- Operations, energy, consumption
- Product requirements
- Material summaries

Usage
=====
* Launch the export from Bill of Materials form/tree-view -> Print -> LCA BOM.  Excel
  exported this way will ignore product variants.
* Or (preferably) click "Print LCA excel" button in the BoM form. This opens up a wizard
  view to select a specific product variant to which according to values are calculated.

Known issues / Roadmap
======================
* Set the amount to seconds in a year in the manufacturing settings. This
  value is used in the calculation of used consumable weight

Credits
=======

Contributors
------------

* Timo Kekäläinen <timo.kekalainen@tawasta.fi>
* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
