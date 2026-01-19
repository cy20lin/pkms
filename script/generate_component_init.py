#!/usr/bin/env python3
import pathlib
import importlib.util
import inspect
import argparse
from typing import Union, Annotated
from pydantic import Field

# ---------- CLI ----------
parser = argparse.ArgumentParser(
    description="Generate nicely formatted __init__.py for a component folder"
)
parser.add_argument(
    "component_dir",
    type=pathlib.Path,
    help="Path to the component folder, e.g., pkg/pkms/component/indexer"
)
parser.add_argument(
    "output_path",
    type=pathlib.Path,
    nargs="?",
    default=None,
    help="Optional output file. If not specified, print to stdout"
)
args = parser.parse_args()
COMPONENT_DIR = args.component_dir
OUTPUT_PATH = args.output_path

# ---------- Helper ----------
def load_module(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def collect_component_classes():
    main_classes, config_classes, runtime_classes = [], [], []

    for py_file in COMPONENT_DIR.glob("_*.py"):
        if not py_file.name.endswith(".py") or py_file.name.startswith("__"):
            continue

        prefix = py_file.stem[1:]  # _HtmlIndexer.py -> HtmlIndexer
        module = load_module(py_file)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if not name.startswith(prefix):
                continue  # 只抓對應 prefix 的 class
            if name.endswith("Config"):
                config_classes.append(name)
            elif name.endswith("Runtime"):
                runtime_classes.append(name)
            else:
                main_classes.append(name)

    return main_classes, config_classes, runtime_classes

def format_union(name, classes, annotated=False):
    lines = []
    if annotated:
        lines.append(f"{name} = Annotated[")
        lines.append(f"    Union[")
    else:
        lines.append(f"{name} = Union[")
    for cls in classes:
        if annotated:
            lines.append(f"        {cls},")
        else:
            lines.append(f"    {cls},")
    if annotated:
        lines.append(f"    ],")
        lines.append(f"    Field(discriminator=\"type\"),")
        lines.append(f"]")
    else:
        lines.append(f"]")
    return "\n".join(lines)

def generate_text(main_classes, config_classes, runtime_classes, component_name):
    component_upper = component_name.capitalize()
    lines = []

    # imports
    for py_file in COMPONENT_DIR.glob("_*.py"):
        if not py_file.name.endswith(".py") or py_file.name.startswith("__"):
            continue
        prefix = py_file.stem[1:]
        module = load_module(py_file)
        classes_in_file = [
            name for name, obj in inspect.getmembers(module, inspect.isclass)
            if name.startswith(prefix)
        ]
        if classes_in_file:
            lines.append(f"from .{py_file.stem} import (")
            for cls in classes_in_file:
                lines.append(f"    {cls},")
            lines.append(")\n")

    lines.append("from typing import Union, Annotated")
    lines.append("from pydantic import Field\n")

    # unions
    lines.append(format_union(f"{component_upper}Union", main_classes))
    lines.append(format_union(f"{component_upper}ConfigUnion", config_classes, annotated=True))
    lines.append(format_union(f"{component_upper}RuntimeUnion", runtime_classes))
    lines.append("")

    # __all__
    all_list = main_classes + config_classes + runtime_classes + [
        f"{component_upper}Union",
        f"{component_upper}ConfigUnion",
        f"{component_upper}RuntimeUnion",
    ]
    lines.append("__all__ = [")
    for name in all_list:
        lines.append(f"    \'{name}\',")
    lines.append("]")

    return "\n".join(lines)

# ---------- Main ----------
def main():
    component_name = COMPONENT_DIR.name
    main_classes, config_classes, runtime_classes = collect_component_classes()
    text = generate_text(main_classes, config_classes, runtime_classes, component_name)

    if OUTPUT_PATH:
        OUTPUT_PATH.write_text(text)
        print(f"[INFO] Generated content written to {OUTPUT_PATH}")
    else:
        print(text)

if __name__ == "__main__":
    main()
