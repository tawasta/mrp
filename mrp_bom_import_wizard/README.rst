.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
BoM Import (Excel/CSV)
======================
This module adds a BoM import wizard that reads **CSV/XLSX** files where **each row equals one BoM line**.
Rows are grouped into a single BoM by **(product_tmpl_id, code, type, product_qty)**.

Key features
------------

- Separate display names for both template and components:
  ``product_tmpl_name`` and ``line_product_name``.
- Set product UoM by ID for template and component:
  ``product_tmpl_uom_id`` and ``line_product_uom_id``.
- Override BoM line UoM by **name** via ``line_product_uom`` (falls back to the component's default).
- Dry-run validation and duplicate-BoM prevention.
- UoM category safety check for BoM line UoM.
- Extensible via small hooks (no need to override ``action_import``): 
  ``extra_required_columns``, ``parse_extra_columns``, ``validate_extra_row``,
  ``mutate_bom_create_vals``, ``mutate_line_create_vals``.

Configuration
=============
- Optional dependency: ``openpyxl`` for reading ``.xlsx/.xlsm`` files. CSV works without it.
- The wizard can create missing products when *Create Missing Products* is enabled (default).
- UoM ID fields must reference existing ``uom.uom`` records.

Usage
=====

1. Open **Manufacturing → Bills of Materials → Import BoM**.
2. Click **CSV template** to download the sample.
3. Fill the file.

   **Required columns**::

     product_tmpl_id, product_qty, code, type, line_product_id, line_product_qty

   **Optional columns**::

     product_tmpl_name, product_tmpl_uom_id,
     line_product_name, line_product_uom_id, line_product_uom

4. Upload the file. Optionally tick **Dry run (validate only)** to verify without creating records.
5. Click **Validate/Import**.

**Example (CSV)**

.. code-block:: csv

   product_tmpl_id,product_tmpl_name,product_tmpl_uom_id,product_qty,code,type,line_product_id,line_product_name,line_product_qty,line_product_uom,line_product_uom_id
   FINISHED-001,My Finished Product,1,1,KIT001,normal,COMP-001,Component A,2,,1
   FINISHED-001,My Finished Product,1,1,KIT001,normal,COMP-002,Component B,3,Units,1
   FINISHED-002,Another Finished,1,1,KIT002,phantom,COMP-003,Component C,1,,1

Known issues / Roadmap
======================
\-

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

