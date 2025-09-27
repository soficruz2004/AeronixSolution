import os
from typing import Any

def load_inputs() -> list[str]:
    files:list[str] = []
    for file in os.listdir("inputs"):
        if file.endswith(".ipc"): files.append(os.path.join("inputs", file))
    assert len(files) > 0, "No input files specified."
    return files

def parse_inputs(files: list[str])->dict[Any,Any]:
    parsed:dict[Any,Any] = {}
    for file in file:
        if 

    return parsed