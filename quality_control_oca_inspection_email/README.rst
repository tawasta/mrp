.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Quality Control OCA: Inspection E-mail
=======================================

* Adds a "Send by E-mail" button to inspections, available once the
  inspection has been completed (state Quality success/Quality
  failed).
* Opens a standard mail composer wizard, pre-filled with a
  dedicated e-mail template and the inspection's PDF report attached
  (via the ``quality_control_oca_inspection_report`` module).
* Adds a "Suggested E-mail Recipients" field
  (``partner_inspection_email_recipient_ids``) used to pre-fill the
  wizard's recipients. Recipients can still be changed freely before
  sending.
* Adds an "Inspection E-mail Sent" field (``inspection_email_sent``),
  automatically set when an e-mail is sent through the wizard, with a
  "Not Sent by E-mail" filter to find inspections not yet
  communicated.
* Exposes an overridable ``_get_default_inspection_email_recipients()``
  hook (returns nothing by default) so other modules can plug in their
  own logic for suggesting recipients - see
  ``quality_control_oca_inspection_email_sale_stock`` for an example
  that suggests the partner of the related sale order.

Configuration
=============
* The e-mail template ("Quality Control: Inspection Results") can be
  freely edited from Settings > Technical > Email Templates.

Usage
=====
* Once an inspection is done, click "Send by E-mail" on the
  inspection form.
* Review/adjust the recipients and message, then send.

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
