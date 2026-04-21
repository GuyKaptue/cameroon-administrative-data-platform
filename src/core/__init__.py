"""
cameroon_population_pipeline/src/core/__init__.py

Core module for the Cameroon population simulation pipeline. This package provides
the foundational logic for geospatial data processing, hierarchical administrative
mapping, demographic simulation (2005-2025), and postal code generation.

The module integrates data from the RGPH 2005 census, GeoBoundaries ADM layers,
and Who's On First (WOF) locality datasets to produce high-fidelity, village-level
population projections.
"""

# Versioning
__version__ = "1.0.0"

# Configuration Access
from .config import config, Config

# Data Loading and Geospatial Processing
from .geospatial_loader import (
    load_geospatial_data,
    get_department_region_mapping
)

# Administrative Hierarchy Management
from .hierarchy_matcher import match_hierarchy
from .hierarchy_builder import build_hierarchy, flatten_hierarchy

# Demographic Logic
from .population_distributor import distribute_population
from .population_simulator import  HierarchicalPopulationSimulator

# Utility and Validation
from .postal_codes import PostalCodeGenerator
from .validator import DataValidator
from .data_exporter import DataExporter

# Define public API
__all__ = [
    "config",
    "Config",
    "load_geospatial_data",
    "get_department_region_mapping",
    "match_hierarchy",
    "build_hierarchy",
    "flatten_hierarchy",
    "distribute_population",
    "HierarchicalPopulationSimulator",
    "PostalCodeGenerator",
    "DataValidator",
    "DataExporter",
]

import logging

# Configure package-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())