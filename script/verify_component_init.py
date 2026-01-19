#!/usr/bin/env python3
import pathlib
import ast
import importlib.util
import inspect
import argparse

# ---------- CLI ----------
parser = argparse.ArgumentParser(
    description="Verify component __init__.py for imports, __all__, and union consistency"
)
parser.add_argument(
    "component_dir",
    type=pathlib.Path,
    help="Path to the component folder, e.g., pkg/pkms/component/indexer"
)
args = parser.parse_args()
COMPONENT_DIR = args.component_dir

# ---------- Helpers ----------
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

    return set(main_classes), set(config_classes), set(runtime_classes)

def parse_init(init_path: pathlib.Path):
    """解析 __init__.py，回傳 imported class, __all__, union assignments"""
    if not init_path.exists():
        return set(), set(), {}
    with init_path.open() as f:
        tree = ast.parse(f.read(), filename=str(init_path))

    imported, all_list, union_assigns = set(), set(), {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            for n in node.names:
                imported.add(n.name)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                all_list.add(elt.value)
                    else:
                        # 假設 union 也是 Assign
                        union_assigns[target.id] = node.value
    return imported, all_list, union_assigns

def extract_union_classes(node):
    """遞迴解析 Annotated / Union / 多層嵌套，回傳 class 名稱列表"""
    result = []

    if isinstance(node, ast.Subscript):
        # Annotated[...] 或 Union[...]
        val_id = getattr(node.value, "id", getattr(node.value, "attr", None))
        # Annotated → 遞迴第一個參數
        if val_id == "Annotated":
            first_arg = node.slice
            # Python 3.9/3.10 AST 差異
            if isinstance(first_arg, ast.Tuple):
                union_node = first_arg.elts[0]
            else:
                union_node = getattr(first_arg, "value", first_arg)
            result.extend(extract_union_classes(union_node))
        elif val_id == "Union":
            # Union[...] 多個類別
            slice_val = node.slice
            if isinstance(slice_val, ast.Tuple):
                for elt in slice_val.elts:
                    if isinstance(elt, ast.Name):
                        result.append(elt.id)
            elif isinstance(slice_val, ast.Name):
                result.append(slice_val.id)
            elif isinstance(slice_val, ast.Subscript):
                # Union[Annotated[...]] 等特殊情況
                result.extend(extract_union_classes(slice_val))
    elif isinstance(node, ast.Name):
        result.append(node.id)
    elif isinstance(node, ast.Tuple):
        for elt in node.elts:
            result.extend(extract_union_classes(elt))
    return result

# ---------- Main ----------
def main():
    component_name = COMPONENT_DIR.name
    main_classes, config_classes, runtime_classes = collect_component_classes()
    init_file = COMPONENT_DIR / "__init__.py"
    imported, all_list, union_assigns = parse_init(init_file)

    print(f"\n# ===== Verifying {component_name} =====")

    # missing import / __all__
    missing_import = (main_classes | config_classes | runtime_classes) - imported
    missing_all = (main_classes | config_classes | runtime_classes) - all_list

    # union names
    union_names = [
        f"{component_name.capitalize()}Union",
        f"{component_name.capitalize()}ConfigUnion",
        f"{component_name.capitalize()}RuntimeUnion",
    ]
    missing_union = {}
    for union_name, expected_classes in zip(
        union_names, [main_classes, config_classes, runtime_classes]
    ):
        if union_name in union_assigns:
            actual_classes = set(extract_union_classes(union_assigns[union_name]))
            missing_union[union_name] = expected_classes - actual_classes
        else:
            missing_union[union_name] = expected_classes

    # report
    if not missing_import and not missing_all and all(not v for v in missing_union.values()):
        print("✅ All classes imported, in __all__, and included in unions")
    else:
        if missing_import:
            print(f"❌ Missing import: {missing_import}")
        if missing_all:
            print(f"❌ Missing in __all__: {missing_all}")
        for union_name, missing in missing_union.items():
            if missing:
                print(f"❌ Missing in union {union_name}: {missing}")

if __name__ == "__main__":
    main()
