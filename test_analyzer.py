#!/usr/bin/env python3
"""
PCB Test Analyzer
Analyzes BOM and coordinate data to identify testing opportunities and issues
"""

from typing import List, Dict, Set, Tuple
import math

# Import the classes from pcb_parser
try:
    from pcb_parser import Component, TestPoint
except ImportError:
    # Fallback if import fails during development
    class Component:
        def __init__(self, designator, part_number, footprint, quantity, description, supplier=""):
            self.designator = designator
            self.part_number = part_number
            self.footprint = footprint
            self.quantity = quantity
            self.description = description
            self.supplier = supplier
    
    class TestPoint:
        def __init__(self, net_name, component_ref, x_coord, y_coord, rotation=0.0):
            self.net_name = net_name
            self.component_ref = component_ref
            self.x_coord = x_coord
            self.y_coord = y_coord
            self.rotation = rotation

class PCBTestAnalyzer:
    """Analyzes PCB data for testing optimization"""
    
    def __init__(self, components: List[Component], test_points: List[TestPoint]):
        self.components = components
        self.test_points = test_points
        self._component_map = {comp.designator: comp for comp in components}
        self._testpoint_map = {tp.net_name: tp for tp in test_points}
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report"""
        report = []
        
        # Basic statistics
        report.append(f"Components in BOM: {len(self.components)}")
        report.append(f"Test Points Available: {len(self.test_points)}")
        
        # Component type breakdown
        component_types = self._analyze_component_types()
        report.append(f"\nComponent Types:")
        for comp_type, count in sorted(component_types.items()):
            report.append(f"  {comp_type}: {count}")
        
        # Critical components that need testing
        critical_components = self._identify_critical_components()
        if critical_components:
            report.append(f"\nCritical Components for Testing:")
            for comp in critical_components