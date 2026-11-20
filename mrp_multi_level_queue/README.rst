.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
MRP Multi Level - Queued
========================

MRP Multi Level with queue jobs.

The MRP run is split into queue jobs per MRP area: cleanup, MRP applicable
calculation, initialisation, one job per low level code and product, and the
final process.

A product MRP area with grouped demand (Nbr. Days greater than 0) is
calculated with the grouped demand method of MRP Multi Level, the same way as
in a standard MRP run.

Configuration
=============
The module adds the scheduled action "Multi Level MRP: Queued" and disables
the default "Multi Level MRP" scheduled action on installation.

Usage
=====
The scheduled action starts the queued MRP run daily. It can also be started
with Run Manually on the scheduled action.

Known issues / Roadmap
======================
* When a product calculation job fails, the products of the next low level
  codes wait in retries, while the LLC reset (after 5 minutes) and the final
  process (after 15 minutes) still run. The MRP run then ends with missing
  planned orders and no error in the MRP inventory.
* The non-grouped demand calculation is a copy of an older MRP Multi Level
  version and does not use its current calculation methods, so the results can
  differ from a standard run (for example for phantom products).
* The order of the low level codes relies on the last queued product job of a
  level running last. With several queue workers, or a level without products,
  the next level can start too early or never.
* The MRP inventory is empty from the cleanup until the final process.

Credits
=======

Contributors
------------
* Jarmo Kortetjärvi <jarmo.kortetjarvi@tawasta.fi>
* Timo Kekäläinen <timo.kekalainen@tawasta.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>


Maintainer
----------

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
