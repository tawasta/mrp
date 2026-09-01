.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Quality Control OCA: Inspection Partner
=======================================

* Adds a Partner field to QC inspections and inspection lines
* The partner is prefilled from the inspection's Reference (`object_id`)
  field using a soft field-name heuristic: it reads `partner_id` /
  `commercial_partner_id` off the referenced record (a sale order, picking etc)
  and handles a direct `res.partner` reference.
* The value stays manually editable if needed. The hand-set partner is kept 
  unless the Reference itself changes.

Configuration
=============
* None needed.

Usage
=====
* Open a QC inspection, and set the Reference field to a partner-bearing document. 
* Partner field fills in automatically; override it by hand if needed.

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
