class BOMParser:
    def parse(self, content):
        return [{"component": "Resistor", "value": "10k", "quantity": 100}]


def parse_inputs(files):
    parsed_data = {
        'bom_components': [],
        'test_points': [],
        'schematics': {},
        'requirements': {},
        'netlist': {}
    }
    
    for file in files:
        if file.type == "BOM":
            parsed_data['bom_components'] = BOMParser().parse(file.content)
        elif file.type == "NETLIST":
            parsed_data['test_points'] = CoordinateParser().parse(file.content)
        elif file.type == "SCHEMATIC":
            parsed_data['schematics'] = SchematicParser().parse(file.content)
        elif file.type == "REQUIREMENTS":
            parsed_data['requirements'] = RequirementsParser().parse(file.content)

    validated_data = PCBDataModel.validate(parsed_data)
    return validated_data
