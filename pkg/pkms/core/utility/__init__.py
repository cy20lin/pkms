import hashlib
import re
import pathlib
from ._sql import (
    extract_sql_params,
    assert_sql_model_aligned
)
from ._CommandParser import CommandParser
from ._SafeNestFormatter import (
    SafeNestFormatter,
    get_nest_item
)
from ._DollarBracesRefResolver import (
    DollarBracesRefResolver
)
from ._BracesRefResolver import (
    BracesRefResolver
)
from ._SimpleFileLocationMatcher import SimpleFileLocationMatcher
from ._FileLocationMatcher import FileLocationMatcher
from ._NestItemGetter import NestItemGetter
from ._SimpleNestItemGetter import SimpleNestItemGetter

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
        raise RuntimeError('Boolean value expected.')

def get_file_content(file_path):
    file = open(file_path, "r", encoding='utf-8')
    content = file.read()
    return content

def get_file_hash_sha256(file_path, chunk_size=4096):
    """
    Calculates the SHA256 hash of a file at the given path.
    """
    # Create a sha256 hash object
    hash_sha256 = hashlib.sha256()
    
    # Open the file in binary read mode ('rb')
    try:
        with open(file_path, 'rb') as f:
            # Read the file in chunks to be memory efficient for large files
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_sha256.update(chunk)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

    # Return the hexadecimal representation of the digest
    return hash_sha256.hexdigest()

def get_content_hash_sha256_string(content):
    # TODO: Figure out if using text content cause potential error
    # TODO: MAYBE accept binary content
    # TODO: MAYBE enable custom encode choice
    # Create a new SHA256 hash object
    hash_object = hashlib.sha256(content.encode('utf-8'))
    # Get the hexadecimal representation of the digest
    hex_digest = hash_object.hexdigest()
    return hex_digest

def get_file_name_id_prefix(file_path):
    p = pathlib.Path(file_path)
    name_id_prefix = p.name.split(' ')[0]
    return name_id_prefix

def is_importance_str(maybe_importance_str:str):
    return all(c == '!' for c in maybe_importance_str)

def try_get_importance(maybe_importance_str:str):
    return len(maybe_importance_str) if is_importance_str(maybe_importance_str) else None

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

def parse_file_name(file_path: str | pathlib.Path):
    '''
    Docstring for parse_file_name
    
    :param file_name: file name with following format
        <file_id_prefix> [importance] [title] {context}<file_extension>
    '''
    p = pathlib.Path(file_path)
    name = p.name
    pattern = r"^([\S]*)\s+(!*)\s*(?:([^\{.]*))(?:{([^}]*)})?[\s\S]*?((:?\.[_a-zA-Z0-9]*)*)$"
    # pattern = r"^([\S]*)\s+(!*)\s*(?:([^\{.]*))(?:{([^}]*)})?[^.]*(.*)$"
    # id: ^([\S]*)
    # space: \s+
    # importance optional: (!*)
    # space: \s*
    # title: (?:([^\{.]*)\s*) , non '{' and '.' character, strip extra space
    # context: (?:{([^}]*)}) , first curlybraces enclosed text
    # rest text: [^.]* , ignored
    # extension: (.*)$ , rest items
    m = re.match(pattern,name)
    if m is not None:
        id = m.group(1)
        importance = m.group(2)
        title = m.group(3)
        context = m.group(4)
        extension = m.group(5)
        # file_id = file_id_prefix + extension
        result = {
            "name": name,
            "id": id,
            "importance": len(importance),
            "title": title,
            "context": context,
            "extension": extension,
        }
    else:
        raise RuntimeError(f'Parsing file_id for file={repr(file_path)} failed')
        
    return result
