from pkms.globber import PathspecGlobber
from pkms.indexer import HtmlIndexer
import json


globber_config = PathspecGlobber.Config(patterns=["**/*.html"], negate=False)
globber = PathspecGlobber(config=globber_config)

html_indexer_config = HtmlIndexer.Config()
html_indexer = HtmlIndexer(config=html_indexer_config)

file_locations = globber.glob(".")


indexed_document = None
for file_location in file_locations:
    try:
        indexed_document = html_indexer.index(file_location)
        print(f'indexed {repr(file_location.path)}, id: {indexed_document.file_id}')
    except Exception as e:
        print(f'skipped {repr(file_location.path)}, reason: {e}')
        print(e.with_traceback())


# print(indexed_document.model_dump_json())