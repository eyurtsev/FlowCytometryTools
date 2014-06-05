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
    FCMeasurement.view_interactively
    FCMeasurement.channel_names
    FCMeasurement.channels
    FCMeasurement.subsample

FCPlate
===========================

.. autosummary::
   :toctree: API

   FCOrderedCollection
   FCPlate 
   FCPlate.from_files
   FCPlate.from_dir
   FCPlate.apply
   FCPlate.plot
   FCPlate.transform
   FCPlate.gate
   FCPlate.counts
   FCPlate.dropna
   FCPlate.subsample

Gates
----------------------------

.. autosummary::
    :toctree: API

    ThresholdGate
    IntervalGate
    QuadGate
    PolyGate 
    FlowCytometryTools.core.gates.CompositeGate 

Transformations
----------------------------

.. autosummary::
    :toctree: API

    FlowCytometryTools.core.transforms.linear
    FlowCytometryTools.core.transforms.hlog
    FlowCytometryTools.core.transforms.tlog


    



