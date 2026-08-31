.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================================
Quality Control OCA: Inspection Sale Order Link
=================================================

* Makes `sale.order` a valid reference target for Quality Control inspections
* Adds a computed, stored `sale_order_id` on inspections and inspection lines.
* Adds an *Inspections* smart button on the sale order form listing the related
  inspections.

When ``quality_control_stock_oca`` and ``sale_stock`` are installed, inspections
that were auto-generated from a delivery are also linked to the originating sale
order (via ``picking_id.sale_id``). Those modules are not hard dependencies.

Configuration
=============
* None needed.

Usage
=====
* Open a sale order. The *Inspections* smart button shows the count of related
  QC inspections and opens the filtered list.
* Create a QC inspection and set its *Reference* to a sale order, or let a
  delivery-triggered inspection link itself automatically.

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
