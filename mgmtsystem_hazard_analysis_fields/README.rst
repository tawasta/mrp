.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Hazard Analysis Fields
======================

Adds the following fields to the Analysis tab of the hazard form:

* **Workcenter**: the existing workcenter field of the hazard
  (mgmtsystem_hazard_risk_workcenter) is moved to the Analysis tab. It is not
  required.
* **Location**: a dropdown of the workcenter categories (mrp.workcenter.category).
  It is required.
* **Supplier**: a dropdown of the partners that are companies and suppliers. The
  suppliers can be limited to the ones that belong to a company that is set in
  the settings. It is not required.

Configuration
=============
* Go to Management System > Configuration > Settings and set the "Supplier
  company" in the Hazard suppliers section. The setting is company-specific.
  Only the suppliers that belong to this company are listed in the supplier of a
  hazard. If the setting is empty, the suppliers of all the companies are listed.

Usage
=====
* Open a hazard and go to the Analysis tab. Select the workcenter, the location
  and the supplier.
* The location is required in the form. A hazard that was created before this
  module has no location, so it has to be selected when the hazard is edited.
* Users who can open hazards can read the workcenter categories.

Known issues / Roadmap
======================
* The material field (product.material) is not included yet.

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
