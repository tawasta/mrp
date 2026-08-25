.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================================================
Quality Control OCA: Inspection E-mail - Default Recipient from Sale Order
==========================================================================

* If QC Inspection was originated from a picking and the picking from
  a Sale order, suggest the related SO's partner as an inspection 
* A glue module connecting `quality_control_oca_inspection_email` with
  `quality_control_stock_oca` and `sale_stock`.
* When an inspection is created for a stock picking that is related to 
  a sale order, the sale order's partner
  is automatically suggested as the inspection e-mail's recipient.
* If the picking has no related sale order, no recipient gets
  suggested by this module

Configuration
=============
* None needed

Usage
=====
* Configure a product trigger that creates a QC inspection when a picking
  is created. Sell that product and go to the picking to see the created 
  inspection as usual. The e-mail recipient has been filled in as a default.

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
