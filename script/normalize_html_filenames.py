import logging
import pathlib
import os
import glob
import datetime
import argparse
from pkms.core.utility import (
    get_file_content,
    index_html_file,
    parse_singlefile_html_metadata,
    get_content_hash_sha256_string,
)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'nil', 'null'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def rename_html_files(base_path, dry_run=True):
    # This Script normalize the webpages html files in the specified directory
    # e.g. base_path = "/path/to/resource/webpages"
    sub_pathes = glob.glob('*.html', root_dir=base_path, recursive=False)

    # f = open('input-names.txt', 'w', newline='\n', encoding='utf-8')
    # for sub_path in sub_pathes:
    #     f.write(sub_path+'\n')

    for sub_path in sub_pathes:
        base_path_ = pathlib.Path(base_path)
        file_path = base_path_ / sub_path
        # print(str(file_path))
        # print(file_path.name)
        name_split = file_path.name.split()
        name_prefix = name_split[0]
        if name_prefix[:4].isdigit():
            index = file_path.name.find(' ')
            name_non_prefix = file_path.name[index:].strip()
        else:
            name_prefix = ''
            name_non_prefix = file_path.name
        index = index_html_file(file_path)
        print(index)
        content = get_file_content(file_path)
        file_hash_sha256 = get_content_hash_sha256_string(content)

        sf_metadata = parse_singlefile_html_metadata(content)
        if isinstance(sf_metadata,dict) and 'saved_date' in sf_metadata:
            saved_datetime = datetime.datetime.fromisoformat(sf_metadata['saved_date'])
        else:
            saved_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
        saved_date = saved_datetime.date().isoformat()
        new_file_prefix = saved_date + '-' + file_hash_sha256[0:8]
        is_same = '1' if new_file_prefix == name_prefix else '0'
        logging.info('rename {}: {} -> {} ;'.format(is_same, name_prefix, new_file_prefix))
        new_file_name = ' '.join([new_file_prefix, name_non_prefix])
        new_file_path = file_path.parent / new_file_name
        try:
            if file_path == new_file_path:
                logging.info(f"skip rename to same file='{file_path}'")
            print(f"mv '{file_path}' '{new_file_path}'")
            if not dry_run:
                os.rename(file_path, new_file_path)
        except FileNotFoundError:
            logging.error(f"Error: The file '{file_path}' was not found.")
        except FileExistsError:
            logging.error(f"Error: The file '{file_path}' already exists.")
        except PermissionError:
            logging.error("Error: Permission denied. Unable to rename the file.")
        except OSError as e:
            logging.error(f"An unexpected OS error occurred: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description='A simple example of parsing options.')
    log_levels = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    parser = argparse.ArgumentParser(description="An example script demonstrating logging with argparse.")
    parser.add_argument(
        '--log-level',
        choices=log_levels,
        default='WARNING',
        help=f"Set the logging level. Choices: {', '.join(log_levels)}. Default: WARNING."
    )
    parser.add_argument('--dir-path', help='The path of the html file dirs to process')
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=True, const=True, nargs='?', type=str2bool)
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # 4. Access the arguments as attributes
    logging.info(f"dir_path: {args.dir_path}")
    logging.info(f"log_level: {args.log_level}")
    logging.info(f"dry_run: {args.dry_run}")
    return args

def main():
    args = parse_args()
    print(args)
    rename_html_files(base_path=args.dir_path, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
