from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, validator
import csv, re, json

@dataclass
class Component:
    designator: str
    part_number: str
    footprint: str
    quantity: int
    description: str
    test_priority: str = "MEDIUM"

@dataclass
class TestPoint:
    net_name: str
    component_ref: str
    x_coord: float
    y_coord: float
    rotation: float = 0.0

class PCBDataModel(BaseModel):
    bom_components: List[Dict]
    test_points: List[Dict]
    schematics: Dict
    requirements: Dict
    netlist: Dict

class BOMParser:
    """Enhanced BOM parser supporting multiple formats"""
    
    def parse(self, content: str) -> List[Component]:
        if content.strip().startswith('<?xml'):
            return self._parse_xml_bom(content)
        elif '\t' in content or ',' in content:
            return self._parse_csv_bom(content)
        else:
            return self._parse_text_bom(content)
    
    def _parse_csv_bom(self, content: str) -> List[Component]:
        components = []
        lines = content.strip().split('\n')
        delimiter = '\t' if '\t' in content else ','
        
        reader = csv.reader(lines, delimiter=delimiter)
        headers = next(reader, [])
        
        for row in reader:
            if len(row) >= 2 and row[0].strip():
                comp = Component(
                    designator=row[0].strip(),
                    part_number=row[1].strip() if len(row) > 1 else "",
                    footprint=row[2].strip() if len(row) > 2 else "",
                    quantity=int(row[3]) if len(row) > 3 and row[3].isdigit() else 1,
                    description=row[4].strip() if len(row) > 4 else "",
                    test_priority=self._assess_component_priority(row[0], row[1] if len(row) > 1 else "")
                )
                components.append(comp)
        return components
    
    def _assess_component_priority(self, designator: str, part_number: str) -> str:
        """AI-based component test priority assessment"""
        critical_patterns = ['POWER', 'RF', 'CRYSTAL', 'CPU', 'MCU', 'LORA']
        high_priority_refs = ['U', 'IC', 'Q', 'T']
        
        if any(pattern in part_number.upper() for pattern in critical_patterns):
            return "HIGH"
        elif designator[0] in high_priority_refs:
            return "HIGH"
        elif designator[0] in ['R', 'C', 'L']:
            return "MEDIUM"
        return "LOW"

class CoordinateParser:
    """Parse test point coordinates from multiple formats"""
    
    def parse(self, content: str) -> List[TestPoint]:
        if content.strip().startswith('D0'):
            return self._parse_ipc_format(content)
        elif 'X=' in content and 'Y=' in content:
            return self._parse_xy_format(content)
        else:
            return self._parse_generic_format(content)
    
    def _parse_ipc_format(self, content: str) -> List[TestPoint]:
        """Parse IPC-356 netlist format"""
        test_points = []
        for line in content.strip().split('\n'):
            if line.startswith('317') or line.startswith('327'):
                parts = line.split()
                if len(parts) >= 3:
                    coords = self._extract_coordinates(parts[2])
                    if coords:
                        tp = TestPoint(
                            net_name=parts[0][3:],  # Remove '317' prefix
                            component_ref=parts[1],
                            x_coord=coords[0],
                            y_coord=coords[1],
                            rotation=coords[2]
                        )
                        test_points.append(tp)
        return test_points
    
    def _extract_coordinates(self, coord_string: str) -> Optional[tuple]:
        """Extract X,Y coordinates from coordinate string"""
        x_match = re.search(r'X([+-]?\d+)', coord_string)
        y_match = re.search(r'Y([+-]?\d+)', coord_string)
        r_match = re.search(r'R(\d+)', coord_string)
        
        if x_match and y_match:
            x = float(x_match.group(1)) / 1000.0
            y = float(y_match.group(1)) / 1000.0
            rotation = float(r_match.group(1)) if r_match else 0.0
            return (x, y, rotation)
        return None

class SchematicParser:
    """Parse schematic files and extract circuit information"""
    
    def parse(self, content: str) -> Dict:
        if content.strip().startswith('<?xml'):
            return self._parse_xml_schematic(content)
        else:
            return self._parse_text_netlist(content)
    
    def _parse_text_netlist(self, content: str) -> Dict:
        """Parse text-based netlist"""
        nets = {}
        components = {}
        
        for line in content.strip().split('\n'):
            if line.startswith('NET'):
                net_info = self._parse_net_line(line)
                if net_info:
                    nets[net_info['name']] = net_info
            elif line.startswith('COMP'):
                comp_info = self._parse_component_line(line)
                if comp_info:
                    components[comp_info['ref']] = comp_info
        
        return {
            'nets': nets,
            'components': components,
            'connections': self._build_connection_matrix(nets, components)
        }
    
    def _parse_net_line(self, line: str) -> Optional[Dict]:
        parts = line.split()
        if len(parts) >= 2:
            return {'name': parts[1], 'connections': []}
        return None
    
    def _parse_component_line(self, line: str) -> Optional[Dict]:
        parts = line.split()
        if len(parts) >= 2:
            return {'ref': parts[1], 'type': 'COMPONENT'}
        return None
    
    def _build_connection_matrix(self, nets: Dict, components: Dict) -> Dict:
        return {'matrix': 'placeholder'}

class RequirementsParser:
    """Parse requirements documents"""
    
    def parse(self, content: str) -> Dict:
        if content.strip().startswith('{'):
            return json.loads(content)
        else:
            return self._parse_text_requirements(content)
    
    def _parse_text_requirements(self, content: str) -> Dict:
        requirements = {
            'functional': [],
            'performance': [],
            'environmental': [],
            'safety': []
        }
        
        current_section = 'functional'
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if 'performance' in line.lower():
                current_section = 'performance'
            elif 'environmental' in line.lower():
                current_section = 'environmental'
            elif 'safety' in line.lower():
                current_section = 'safety'
            else:
                requirements[current_section].append(line)
        
        return requirements

def detect_file_type(filepath: str, content: str = "") -> str:
    """Intelligent file type detection"""
    ext = filepath.lower().split('.')[-1]
    
    # Extension-based detection
    if ext in ['csv', 'tsv']:
        return "BOM"
    elif ext in ['ipc', 'net']:
        return "NETLIST"
    elif ext in ['schdoc', 'sch']:
        return "SCHEMATIC"
    elif ext in ['txt', 'md', 'docx']:
        if 'requirement' in filepath.lower():
            return "REQUIREMENTS"
        elif any(keyword in content.upper() for keyword in ['NET', 'COMPONENT', 'CONN']):
            return "NETLIST"
    
    # Content-based detection
    if content:
        if 'designator' in content.lower() or 'part' in content.lower():
            return "BOM"
        elif content.startswith('317') or content.startswith('327'):
            return "NETLIST"
        elif '<?xml' in content and 'schematic' in content.lower():
            return "SCHEMATIC"
    
    return "UNKNOWN"

def parse_inputs(files: List[Dict]) -> Dict[str, Any]:
    """Enhanced multi-format parser with validation"""
    parsed_data = {
        'bom_components': [],
        'test_points': [],
        'schematics': {},
        'requirements': {},
        'netlist': {},
        'metadata': {
            'total_files': len(files),
            'file_types': {},
            'parsing_errors': []
        }
    }
    
    # Initialize parsers
    parsers = {
        'BOM': BOMParser(),
        'NETLIST': CoordinateParser(),
        'SCHEMATIC': SchematicParser(),
        'REQUIREMENTS': RequirementsParser()
    }
    
    for file in files:
        try:
            file_type = detect_file_type(file['path'], file.get('content', ''))
            parsed_data['metadata']['file_types'][file['path']] = file_type
            
            if file_type in parsers:
                parser = parsers[file_type]
                result = parser.parse(file['content'])
                
                if file_type == "BOM":
                    parsed_data['bom_components'].extend(result)
                elif file_type == "NETLIST":
                    parsed_data['test_points'].extend(result)
                elif file_type == "SCHEMATIC":
                    parsed_data['schematics'][file['path']] = result
                elif file_type == "REQUIREMENTS":
                    parsed_data['requirements'][file['path']] = result
                    
        except Exception as e:
            error_info = {
                'file': file['path'],
                'error': str(e),
                'type': 'parsing_error'
            }
            parsed_data['metadata']['parsing_errors'].append(error_info)
    
    # Post-processing: Link components to test points
    parsed_data = _link_components_to_testpoints(parsed_data)
    
    # Validate with Pydantic
    try:
        validated_data = PCBDataModel(**parsed_data)
        return validated_data.dict()
    except Exception as e:
        parsed_data['metadata']['validation_errors'] = [str(e)]
        return parsed_data

def _link_components_to_testpoints(data: Dict) -> Dict:
    """Create relationships between components and test points"""
    component_map = {comp.designator: comp for comp in data['bom_components']}
    
    for tp in data['test_points']:
        if tp.component_ref in component_map:
            tp.linked_component = component_map[tp.component_ref]
    
    return data