.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Quality Control OCA: Inspection Manual Product
==============================================


* Allow setting the inspected product manually when it can't be derived
  from the reference field
* Still auto-fills from the inspection's Reference (`object_id`) when that
  is a product, a stock move or a lot, and a hand-set value is kept when the
  Reference changes to something that has no product (e.g. a sale order).
* The product may be left empty.
* When the Reference *does* identify a product (a product, stock move or lot),
  the field stays locked to it: changing it by hand raises a ``ValidationError``.
* Intended for inspections created from a sale order (via
  `quality_control_oca_inspection_sale_link`) where the user still needs
  to record which product was inspected, e.g. for showing the product on the
  `quality_control_oca_inspection_report` PDF print.

Configuration
=============
* None needed.

Usage
=====
* Open an inspection whose Reference is not a product (a sale order, ...). The
  Product field is now editable - pick the inspected product, or leave it empty.

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
