from pkms.globber import PathspecGlobber
from pkms.indexer import HtmlIndexer
from pkms.upserter import Sqlite3Upserter
import json


globber_config = PathspecGlobber.Config(
    patterns=["**/*.html"], 
    negate=False
)
globber = PathspecGlobber(config=globber_config)

html_indexer_config = HtmlIndexer.Config()
html_indexer = HtmlIndexer(config=html_indexer_config)

upserter_config = Sqlite3Upserter.Config(
    db_path='spike-pkms.db'
)
upserter = Sqlite3Upserter(config=upserter_config)

collection_path = '.'
file_locations = globber.glob(collection_path)

# print('')    
# print("=== BEGIN index ===")
# print('')    

# indexed_document = None
# documents = []
# for file_location in file_locations:
#     try:
#         indexed_document = html_indexer.index(file_location)
#         print(f'success index: {repr(file_location.path)}, id: {indexed_document.file_id}')
#         documents.append(indexed_document)
#     except Exception as e:
#         print(f'skipped index: {repr(file_location.path)}, reason: {e}')
#         # print(e.with_traceback())
# print('')    
# print("=== BEGIN upsert ===")
# print('')    

# for indexed_document in documents:
#     try:
#         upserter.upsert(indexed_document)
#         print(f'success upsert: {indexed_document.file_id}')
#     except Exception as e:
#         print(f'skipped upsert: {indexed_document.file_id}, reason: {e}')


indexed_document = None
documents = []
for file_location in file_locations:
    try:
        indexed_document = html_indexer.index(file_location)
        upserter.upsert(indexed_document)
        print(f'success index: {repr(file_location.path)}, id: {indexed_document.file_id}')
        documents.append(indexed_document)
    except Exception as e:
        print(f'skipped index: {repr(file_location.path)}, reason: {e}')
        # print(e.with_traceback())
