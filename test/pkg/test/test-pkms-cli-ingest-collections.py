import os
import os.path
import pytest
from pkms.cli import ingest
import pathlib

def test_pkms_cli_ingest_collections():
    test_dir = pathlib.Path(__file__).parents[2]
    test_config_path = test_dir / 'data' / 'ingest-collections.jsonc'
    test_working_dir = test_dir / 'tmp' / 'ingest-collections'
    test_result_db_path = test_working_dir / 'pkms.db'
    os.makedirs(test_working_dir, exist_ok=True)
    test_result_db_path.unlink(missing_ok=True)
    os.chdir(test_working_dir)
    argv = [
        ingest.__file__, f'{test_config_path}'
    ]
    assert ingest.main(argv) == 0
    assert test_result_db_path.is_file()
    assert test_result_db_path.stat().st_size > 0