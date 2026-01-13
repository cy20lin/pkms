from pkms.globber import PathspecGlobber
from pkms.indexer import HtmlIndexer
from pkms.upserter import Sqlite3Upserter
import commentjson as json

def ingest_html_collection(collection_path, db_path, dry_run):
    globber_config = PathspecGlobber.Config(
        patterns=["**/*.html"], 
        negate=False
    )
    globber = PathspecGlobber(config=globber_config)

    html_indexer_config = HtmlIndexer.Config()
    html_indexer = HtmlIndexer(config=html_indexer_config)

    upserter_config = Sqlite3Upserter.Config(
        db_path= db_path # 'spike-pkms.db'
    )
    upserter = Sqlite3Upserter(config=upserter_config)

    file_locations = globber.glob(collection_path)

    indexed_document = None
    documents = []
    for file_location in file_locations:
        try:
            if dry_run:
                print(f'process index: {repr(file_location.path)}')
                continue
            indexed_document = html_indexer.index(file_location)
            upserter.upsert(indexed_document)
            print(f'success index: {repr(file_location.path)}, id: {indexed_document.file_id}')
            documents.append(indexed_document)
        except Exception as e:
            print(f'skipped index: {repr(file_location.path)}, reason: {e}')
            # print(e.with_traceback())

import argparse
import sys

def str_to_bool(s: str):
    if s.isupper():
        ss = s.lower()
    else:
        ss = s[0].lower() + s[1:]
    if ss in ('1','y','t','yes','true','on'):
        return True
    elif ss in ('0','n','f','no','false','off'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser("Ingest specified collection of owned file resources")
    parser.add_argument("config_path")
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=None, const=True, nargs='?', type=str_to_bool)
    parser.add_argument('--verbose', help='Print Verbosely',default=True, const=True, nargs='?', type=str_to_bool)
    return parser.parse_args(argv[1:])
    
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    db_path: Optional[str] = None
    collection_path: Optional[str] = None
    dry_run: Optional[bool] = False

    
def main(argv):
    args = parse_args(argv)
    config_json = {}
    print(args.config_path)
    with open(args.config_path, 'r') as f:
        config_json = json.load(f)
    config = Config(**config_json)
    if args.dry_run is not None:
        # override the config setting
        config.dry_run = args.dry_run
    ingest_html_collection(**config.model_dump())
    return 0

if __name__ == '__main__':
    argv = sys.argv
    code = main(argv)
    sys.exit(code)