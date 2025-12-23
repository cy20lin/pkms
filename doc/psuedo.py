# date: 2025-12-22
import re
import pathlib

def get_file_extension(file_name):
    '''
    extract full extension from filename,
    extension should not contains special characters like spaces
    '''
    m = re.match(r"^[\s\S]*?((:?\.[_a-zA-Z0-9]*)*)$", file_name)
    if len(m.groups()) >= 2:
        return m.group(1)
    else:
        return ''

app_config = Config.parse_config(args.config_path)

for i,collection_config in enumerate(app_config.collections):
    globber = GlobberBuilder.from_config(collection_config.globber)

    # Glob files in specified base_path
    file_pathes = globber.glob()

    # Walk through all file_path and get all file extensions
    file_extension_set = set()
    for file_path in file_pathes:
        file_extension = get_file_extension(file_path)
        file_extension_set.add(file_extension)

    # Prepare indexers 
    # MAYBE add options for enabling prepare indexer on demand ? 
    indexer_map = {}
    for key in file_extension_set:
        global_indexer_config = app_config.indexer_mapping.get(key, None)
        local_indexer_config = collection_config.indexer_mapping(key, None)
        indexer_config = merge_indexer_configs([
            pkms.indexer.builtin_indexer_config,
            global_indexer_config,
            local_indexer_config
        ])
        indexer = indexer_builder.build_indexer(indexer_config)
        indexer_map[key] = indexer
    
    # Prepare Upserter
    upserter_config = collection_config.upserter
    upserter = upserter_builder.build_upserter(upserter_config)
    
    # File indexing + upsert
    for file_path in file_pathes:
        file_extension = get_file_extension(file_path)
        indexer = indexer_map[key]
        index = indexer.index(file_path)
        upserter.upsert(index)

# Date: 2025-12-22
# upserter_builder
# MAYBE rename to DatabaseAccessor? for more generic db operation for now
# OR just use DatabaseUpserter, (i think prefer this for now)
# Date: 2025-12-23
# Decision: Let that be Upserter

# Date: 2025-12-22
# Maybe add cache capability to indexer_builder (maybe rename to IndexerRegistry,
# and have a method call build ?), same applies to other classes
# Date: 2025-12-23
# Decision: Use Indexer Registry





