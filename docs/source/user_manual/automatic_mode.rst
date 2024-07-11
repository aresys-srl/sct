.. _sct_auto:

Automatic Analyses Detection Mode
=================================

SCT can be used to automatically process a given input product without selecting the specific analysis to be performed but
letting the software decide all the available analyses that applies to the product itself based on its footprint.

This mechanism requires an external .json file called Calibration Sites Registry that must be provided to
the ``sct_automatic_analysis()`` function available in ``sct.analyses.automatic_analyses``. This file must be compliant with
the internal schema for validation purposes and contains several calibration sites with their Latitude/Longitude bounding
corners, a list of analyses commonly associated with those sites and additional reference files such as Point Target locations.

This is a generic example of th structure of the registry:

.. code-block:: json

    "regions": {
        "surat_basin": {
            "description": "Surat Basin, Queensland, Australia",
            "latitude_boundaries_deg": [
                -28,
                -25
            ],
            "longitude_boundaries_deg": [
                149,
                152
            ],
            "supported_analyses": [
                "point_target_analysis"
            ],
            "reference_dataset": "path/to/point/target/csv"
        },
        "rosamond": {
            "description": "Rosamond Corner Reflector Array, Rosamond Dry Lakebed, California, USA",
            "latitude_boundaries_deg": [
                34,
                35
            ],
            "longitude_boundaries_deg": [
                -119,
                -117
            ],
            "supported_analyses": [
                "point_target_analysis"
            ],
            "reference_dataset": "path/to/point/target/csv"
        },
        "rain_forest_amazon": {
            "description": "Rain Forest, Amazon",
            "latitude_boundaries_deg": [
                -10,
                -4
            ],
            "longitude_boundaries_deg": [
                -71,
                -65
            ],
            "supported_analyses": [
                "radiometric_profiles",
                "scalloping"
            ],
            "output_radiometric_quantity": "gamma_nought"
        },
    }

This means that when an input product is passed to this function, SCT checks the intersection of its footprint with those
of the registry's calibration sites, selects the proper one and perform all the analyses expected for that site.

This feature can be pretty useful to automate batch analyses or analyses on products recorded at known calibration sites.
