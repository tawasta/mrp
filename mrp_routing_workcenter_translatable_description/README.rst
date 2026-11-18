.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Translatable Description in MRP Operations
==========================================

Make Description of MRP Operation translatable.

* The operation form has a Description tab with a translatable description
* The work order form shows the description of its operation on the Work
  Instruction tab

Changes in 19.0
===============
Odoo 19.0 removed the Description field (note) of MRP operations and the work
instruction of work orders. This module recreates the field with the same name
and type as in 17.0 (translatable HTML), so that the descriptions and their
translations of a 17.0 database are kept when the database is upgraded, for
example with OpenUpgrade.

The PDF and Google Slide work sheets of 17.0 are not recreated.

Fixed compared to 17.0: when the description of an operation was cleared, the
editor left empty markup and the work order showed an empty Work Instruction
tab. In 19.0 the tab is hidden when the description is empty.

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
* In 17.0 the description was hidden when the work sheet type was PDF or Google
  Slide. In 19.0 such old descriptions are shown again on the operation and the
  work order.

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
