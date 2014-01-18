.. _api:

.. currentmodule:: FlowCytometryTools

Containers
----------------------------

FCMeasurement
===========================

.. autosummary::
    :toctree: API

    FCMeasurement
    FCMeasurement.apply
    FCMeasurement.plot
    FCMeasurement.transform
    FCMeasurement.gate
    FCMeasurement.counts
    FCMeasurement.get_data
    FCMeasurement.view
    FCMeasurement.channel_names
    FCMeasurement.channels

FCPlate
===========================

.. autosummary::
   :toctree: API

   FCPlate 
   FCPlate.from_files
   FCPlate.from_dir
   FCPlate.apply
   FCPlate.plot
   FCPlate.transform
   FCPlate.gate
   FCPlate.counts
   FCPlate.dropna

Gates
----------------------------

.. autosummary::
    :toctree: API

    ThresholdGate
    IntervalGate
    QuadGate
    PolyGate 


Transformations
----------------------------

.. autosummary::
    :toctree: API

    FlowCytometryTools.core.transforms.linear
    FlowCytometryTools.core.transforms.hlog
    FlowCytometryTools.core.transforms.tlog


    



