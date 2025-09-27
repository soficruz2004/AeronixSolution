#!/usr/bin/env python3
"""
PCB Data Parsers
Handles parsing of BOM (Bill of Materials) and coordinate data
"""

import csv
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Component:
    """Represents a component from the BOM"""
    designator: str
    part_number: str
    footprint: str
    quantity: int
    description: str
    supplier: str = ""
    
    def __str__(self):
        return f"{self.designator}: {self.part_number} ({self.footprint})"

@dataclass
class TestPoint:
    """Represents a test point with coordinates"""
    net_name: str
    component_ref: str
    x_coord: float
    y_coord: float
    rotation: float = 0.0
    
    def __str__(self):
        return f"{self.net_name} @ ({self.x_coord:.2f}, {self.y_coord:.2f})"

class BOMParser:
    """Parser for Bill of Materials data"""
    
    def parse_file(self, filepath: str) -> List[Component]:
        """Parse BOM from CSV file"""
        components = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect if it's CSV or Excel-exported format
                sample = file.read(1024)
                file.seek(0)
                
                if '\t' in sample:
                    delimiter = '\t'
                else:
                    delimiter = ','
                
                reader = csv.reader(file, delimiter=delimiter)
                
                # Skip header row
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 4 and row[0].strip():  # Ensure we have enough columns
                        try:
                            component = Component(
                                designator=row[0].strip(),
                                part_number=row[1].strip() if len(row) > 1 else "",
                                footprint=row[2].strip() if len(row) > 2 else "",
                                quantity=int(row[3]) if len(row) > 3 and row[3].strip().isdigit() else 1,
                                description=row[4].strip() if len(row) > 4 else "",
                                supplier=row[5].strip() if len(row) > 5 else ""
                            )
                            components.append(component)
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Skipping invalid row: {row[:3]}... ({e})")
                            continue
                            
        except FileNotFoundError:
            print(f"Error: Could not find BOM file: {filepath}")
        except Exception as e:
            print(f"Error parsing BOM file: {e}")
            
        return components
    
    def parse_from_strings(self, data_lines: List[str]) -> List[Component]:
        """Parse BOM from list of strings (for manual input)"""
        components = []
        
        for line in data_lines:
            parts = line.split('\t') if '\t' in line else line.split(',')
            if len(parts) >= 3:
                try:
                    component = Component(
                        designator=parts[0].strip(),
                        part_number=parts[1].strip(),
                        footprint=parts[2].strip(),
                        quantity=int(parts[3]) if len(parts) > 3 and parts[3].strip().isdigit() else 1,
                        description=parts[4].strip() if len(parts) > 4 else ""
                    )
                    components.append(component)
                except (ValueError, IndexError):
                    continue
                    
        return components

class CoordinateParser:
    """Parser for coordinate/pick-and-place data"""
    
    def parse_file(self, filepath: str) -> List[TestPoint]:
        """Parse coordinates from text file"""
        test_points = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    test_point = self._parse_coordinate_line(line)
                    if test_point:
                        test_points.append(test_point)
                    else:
                        print(f"Warning: Could not parse line {line_num}: {line[:50]}...")
                        
        except FileNotFoundError:
            print(f"Error: Could not find coordinate file: {filepath}")
        except Exception as e:
            print(f"Error parsing coordinate file: {e}")
            
        return test_points
    
    def _parse_coordinate_line(self, line: str) -> Optional[TestPoint]:
        """Parse a single coordinate line"""
        # Expected format: NET_NAME    COMPONENT_REF    COORDINATE_STRING
        parts = line.split()
        
        if len(parts) < 3:
            return None
            
        net_name = parts[0]
        component_ref = parts[1]
        coord_string = parts[2]
        
        # Parse coordinate string format: D0374PA00X+070015Y-039840X0610Y0610R090S0
        coords = self._extract_coordinates(coord_string)
        
        if coords:
            x, y, rotation = coords
            return TestPoint(
                net_name=net_name,
                component_ref=component_ref,
                x_coord=x,
                y_coord=y,
                rotation=rotation
            )
        
        return None
    
    def _extract_coordinates(self, coord_string: str) -> Optional[Tuple[float, float, float]]:
        """Extract X, Y coordinates and rotation from coordinate string"""
        try:
            # Look for X coordinate (X+/-NNNNN or X+/-NNNNNN)
            x_match = re.search(r'X([+-]?\d+)', coord_string)
            # Look for Y coordinate  
            y_match = re.search(r'Y([+-]?\d+)', coord_string)
            # Look for rotation
            r_match = re.search(r'R(\d+)', coord_string)
            
            if x_match and y_match:
                # Convert from what appears to be 10ths of units to regular units
                x = float(x_match.group(1)) / 1000.0  # Assuming coordinates in 1000ths
                y = float(y_match.group(1)) / 1000.0
                rotation = float(r_match.group(1)) if r_match else 0.0
                
                return (x, y, rotation)
                
        except (ValueError, AttributeError):
            pass
            
        return None
    
    def parse_from_strings(self, data_lines: List[str]) -> List[TestPoint]:
        """Parse coordinates from list of strings"""
        test_points = []
        
        for line in data_lines:
            test_point = self._parse_coordinate_line(line.strip())
            if test_point:
                test_points.append(test_point)
                
        return test_points

class SchematicParser:
    """Parser for schematic files (placeholder for future expansion)"""
    
    def parse_file(self, filepath: str) -> Dict:
        """Parse schematic file - placeholder implementation"""
        return {
            "nets": [],
            "components": [],
            "connections": []
        }

# Example usage and testing
if __name__ == "__main__":
    print("Testing PCB Parsers...")
    
    # Test BOM parser with sample data
    sample_bom = [
        "TP_SD40\tTP,PB6,TP_LCMOD,TP_XT1,TP_5,ORIGING,TP_PB5,TP_2,TP_USBVCC0,TP_DTR0,GND,TP1,T1,TP-SP\t61\tTP-SP",
        "IOH0\tIOH0\t1X10\t1\t10x1F-H8.5",
        "C6,C2,C1,C4,C7,C5,C10\tC0603_ROUND\t7\t100n"
    ]
    
    bom_parser = BOMParser()
    components = bom_parser.parse_from_strings(sample_bom)
    
    print(f"\nParsed {len(components)} components:")
    for comp in components[:3]:  # Show first 3
        print(f"  {comp}")
    
    # Test coordinate parser with sample data
    sample_coords = [
        "317MISO ICSP0 D0374PA00X+070015Y-039840X0610Y0610R090S0",
        "317+5V ICSP0 D0374PA00X+071015Y-039840X0610Y0610R090S0",
        "327GND RESET0-1 A01X+045811Y-031504X0630Y0551R000S2"
    ]
    
    coord_parser = CoordinateParser()
    test_points = coord_parser.parse_from_strings(sample_coords)
    
    print(f"\nParsed {len(test_points)} test points:")
    for tp in test_points:
        print(f"  {tp}")