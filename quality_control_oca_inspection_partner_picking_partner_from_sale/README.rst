.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================================================
"Quality Control OCA: Inspection Partner from Picking's Sale Order
==================================================================

* By default try to fill the QC inspection partner from the picking's SO
  for stock-triggered inspections
* When a QC inspection references a stock move or a picking, its Partner ``partner_id``
  is filled from the picking's SO's customer, falling back to the picking's own
  `partner_id` field when there is no sale order.
* Intended to solve the issue where the relevant Partner for a QC inspection
  is usually the actual customer of the original sale, and not the delivery 
  address of the delivery order.

Configuration
=============
* None needed

Usage
=====
* Trigger or create an inspection from a delivery that originates from a sale. 
  QC Insepction's Partner gets filled with the SO's customer.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
        :alt: Futural Oy
        :target: https://futural.fi/

This module is maintained by Futural Oy
