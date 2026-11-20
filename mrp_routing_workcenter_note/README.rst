.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Adds Description field to MRP Operation
=======================================

The module adds translatable Description field to MRP Operations.

* The operation form has a Description tab with a translatable description
* The work order form shows the description of its operation on the Work
  Instruction tab

Changes in 19.0
===============
The module was renamed from mrp_routing_workcenter_translatable_description to
mrp_routing_workcenter_note.

Odoo 19.0 removed the Description field (note) of MRP operations and the work
instruction of work orders. This module recreates the field with the same name
and type as in 17.0 (translatable HTML), so that the descriptions and their
translations of a 17.0 database are kept when the database is upgraded, for
example with OpenUpgrade.

Configuration
=============
None needed

Usage
=====
Write the description on the Description tab of an MRP operation. Write the
translations with the language button of the field.

Known issues / Roadmap
======================
* The descriptions are kept only if the upgrade keeps the note column of the
  operations until this module is installed in 19.0. Check this with the actual
  upgrade chain (also the 18.0 step) before upgrading a production database.

Credits
=======

Contributors
------------

* Timo Kekäläinen <timo.kekalainen@tawasta.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
