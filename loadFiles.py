import os

def load_inputs():
    files:list[str] = []
    for file in os.listdir("inputs"):
        for i in ["netlist", "bom", "schematic", "req_doc"]:
            if file.endswith(i): files.append(os.path.join("inputs", file))
    assert len(files) > 0, "No input files specified."
    return files
