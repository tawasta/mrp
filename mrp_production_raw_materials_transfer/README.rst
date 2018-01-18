.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Raw Material Transfer for Manufacturing Orders
==============================================

* Adds a button to Manufacturing Order view for quick transfer of raw materials from another location to manufacturing location
* The button is a shortcut to making an Internal Transfer containing the missing raw materials.

Configuration
=============
* Configure the internal transfer picking type and default source location in Manufacturing -> Settings

Usage
=====
* Click the "Transfer Materials" button in Manufacturing Order form view when raw materials are unavailable for the MO
* After confirming the internal transfer, click Check Availability for the MO to see updated raw material quantities

Known issues / Roadmap
======================
* Error messages shown for missing MRP configuration do not currently contain a link to the MRP settings view, navigating there has to be done manually

Credits
=======

Contributors
------------
* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.