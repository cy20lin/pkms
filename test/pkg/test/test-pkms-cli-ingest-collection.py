import os
import os.path
import pytest
from pkms.cli import ingest
import pathlib
import shutil
import filecmp
import sqlite3

def try_copy_file(src_file, dst_file):
    if not dst_file.exists() or not filecmp.cmp(src_file, dst_file, shallow=False):
        shutil.copy2(src_file, dst_file)
        print(f"'{src_file.name}' copied.")
        return True
    else:
        print(f"'{dst_file.name}' is up to date.")
        return False

def test_pkms_cli_ingest_file():
    test_dir = pathlib.Path(__file__).parents[2]
    test_config_path = test_dir / 'data' / 'ingest-config.jsonc'
    test_workspace_dir = test_dir / 'tmp' / 'ingest-collection'
    test_workspace_config_path = test_workspace_dir / "config.jsonc"
    test_working_dir = test_workspace_dir
    test_result_db_path = test_working_dir / 'index.db'
    test_collections_path = test_dir / 'data' / 'collections'
    test_collection1_path = test_collections_path / 'html' 
    test_collection2_path = test_collections_path / 'odt' 
    os.makedirs(test_working_dir, exist_ok=True)
    test_result_db_path.unlink(missing_ok=True)
    os.chdir(test_working_dir)
    try_copy_file(test_config_path, test_workspace_config_path)
    argv = [
        ingest.collection.__file__, 
        test_collection1_path.as_posix(),
        '--workspace-dir', test_workspace_dir.as_posix(),
        '--config-path', test_workspace_config_path.as_posix(),
    ]
    assert ingest.collection.main(argv) == 0
    assert test_result_db_path.is_file()
    assert test_result_db_path.stat().st_size > 0

    # Tests for index.db
    conn = sqlite3.connect(test_result_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files")
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert {row["file_id"] for row in rows} == {
        '0001-01-01-0001',
        '2026-01-18-1604b853',
    }


if __name__ == '__main__':
    import sys
    argv = sys.argv
    code = pytest.main(argv)
    sys.exit(code)