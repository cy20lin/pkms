import os
import os.path
import pytest
from pkms.cli import ingest
import pathlib
import shutil
import filecmp

def test_pkms_cli_ingest_workspace():
    test_dir = pathlib.Path(__file__).parents[2]
    test_config_path = test_dir / 'data' / 'ingest-collections.jsonc'
    test_workspace_dir = test_dir / 'tmp' / 'ingest-collections'
    test_workspace_config_path = test_workspace_dir / "config.jsonc"
    test_working_dir = test_workspace_dir
    test_result_db_path = test_working_dir / 'index.db'
    os.makedirs(test_working_dir, exist_ok=True)
    test_result_db_path.unlink(missing_ok=True)
    os.chdir(test_working_dir)
    argv = [
        ingest.workspace.__file__, 
        '--workspace-dir', test_workspace_dir.as_posix(),
        '--config-path', test_config_path.as_posix(),
    ]
    assert ingest.workspace.main(argv) == 0
    assert test_result_db_path.is_file()
    assert test_result_db_path.stat().st_size > 0