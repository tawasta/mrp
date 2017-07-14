.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Archived Product List for BOMs
==============================

Adds a new notebook page to BOMs for showing all archived products it contains and for indicating if a BOM cleanup is needed. The calculation is run periodically by a scheduled task.

Installation
============
* Just install this module

Configuration
=============
* Configure the scheduled task frequency in settings. By default it runs every six hours.

Usage
=====
* Navigate to BOM view and use filters to list BOMs that have archived products
* If you need up-to-date info you can do a manual recalculation for all BOMs in Manufacturing menu, or for a single BOM in the Bill of Materials form view 

Known issues / Roadmap
======================
* It would be way more user-friendly if the archived product info was readily available in the BOM form view as an up-to-date computed field. 
However iterating the whole BOM structure using core's child_line_ids computed field on the fly while using another computed field causes 
a KeyError in cache, which is somehow related to this issue/comment: https://github.com/odoo/odoo/issues/7326#issuecomment-160159561.
Putting the calculation behind a button click solves this but is slightly clunky to use.

Credits
=======

Contributors
------------
* Timo Talvitie <timo@vizucom.com>

Maintainer
----------
.. image:: http://vizucom.com/logo.png
   :alt: Vizucom Oy
   :target: http://www.vizucom.com


This module is maintained by Vizucom Oy