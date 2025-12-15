import datetime
import hashlib
import re
import logging
import argparse
import inscriptis
import pathlib
import json
from bs4 import BeautifulSoup
from html_to_markdown import convert




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
    parser.add_argument('file_path', help='The path of the html file to process')
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # 4. Access the arguments as attributes
    logging.info(f"file_path: {args.file_path}")
    logging.info(f"log_level: {args.log_level}")
    return args

MONTH_MAP = {
    "jan": "01", "january": "01", "janvier": "01", "一月": "01",
    "feb": "02", "february": "02", "février": "02", "二月": "02",
    "mar": "03", "march": "03", "mars": "03", "三月": "03",
    "apr": "04", "april": "04", "avril": "04", "四月": "04",
    "may": "05", "mai": "05", "五月": "05",
    "jun": "06", "june": "06", "juin": "06", "六月": "06",
    "jul": "07", "july": "07", "juillet": "07", "七月": "07",
    "aug": "08", "august": "08", "août": "08", "八月": "08",
    "sep": "09", "september": "09", "septembre": "09", "九月": "09",
    "oct": "10", "october": "10", "octobre": "10", "十月": "10",
    "nov": "11", "november": "11", "novembre": "11", "十一月": "11",
    "dec": "12", "december": "12", "décembre": "12", "十二月": "12",
}

def parse_js_date_to_iso8601(date_str: str) -> str:
    """
    Convert a JavaScript Date.toString()-style string into ISO 8601 format.
    Example input: "Sun May 12 2024 23:16:00 GMT+0800 (Taipei Standard Time)"
    Output: "2024-05-12T23:16:00+08:00"
    """

    # Remove timezone name in parentheses
    cleaned = date_str.split(" (")[0]

    # Split into tokens
    tokens = cleaned.split()

    # Extract parts (ignore weekday at index 0)
    month_token = tokens[1].lower()
    yyyy = tokens[3]
    dd = tokens[2]
    hhmmss = tokens[4]

    # Normalize month
    mm = MONTH_MAP.get(month_token)
    if not mm:
        raise ValueError(f"Unknown month name: {tokens[1]}")

    # Normalize zone (strip 'GMT' and insert colon for ISO compliance)
    zone = tokens[5]
    zone = zone.replace("GMT", "").replace(":","")
    zone = zone[:3] + ":" + zone[3:]
    if len(zone) != 6:
        raise RuntimeError(f'Cannot parse timezone {repr(tokens[5])}')

    # Build ISO 8601 string
    return f"{yyyy}-{mm}-{dd}T{hhmmss}{zone}"

def parse_singlefile_info_text(info_text):
    records = info_text.split('\n')
    info = {}
    for i,r in enumerate(records):
        has_key = False
        sep = r.find('=')
        if sep < 0: 
            sep = r.find(':')
        if sep >= 0:
            key = r[0:sep]
            value = r[sep+1:]
        else:
            key = str(i+1)
            value = r
        # replace '-' to '_'
        key = re.sub(r'[^a-zA-Z0-9_]', '_', key)
        info[key] = value

    return info


def get_file_content(file_path):
    file = open(file_path, "r", encoding='utf-8')
    content = file.read()
    return content

def get_html_title(html_content):
    # Pattern explanation:
    # <title.*?> : Matches the opening <title> tag and any attributes (non-greedy)
    # (.+?)      : Captures the content of the title (capture group 1, non-greedy)
    # </title>   : Matches the closing tag
    pattern = re.compile(r'<title.*?>(.+?)</title>', re.IGNORECASE | re.DOTALL)
    match = pattern.search(html_content)
    title = match.group(1) if match else None
    return title

def get_content_hash_sha256_string(content):
    # Create a new SHA256 hash object
    hash_object = hashlib.sha256(content.encode('utf-8'))
    # Get the hexadecimal representation of the digest
    hex_digest = hash_object.hexdigest()
    return hex_digest

def parse_singlefile_html_metadata(content, parse_info_text=True, normalize_saved_date=True):
    # sf_marker = "Page saved with SingleFile"
    sf_marker = " SingleFile"
    sf_comment = re.search(f"<!--[\\s\\S]*{sf_marker}([\\s\\S]*?)-->", content)
    is_sf_html = sf_comment is not None
    if is_sf_html:
        # logging.debug(sf_comment)
        sf_metadata_content = sf_comment.group(1)
        end = sf_comment.end(1)
        matches = re.finditer("\n\s+([_A-Za-z0-9\\- ]+): *", sf_metadata_content)
        key = None
        value_start = None
        value_end = None
        data = {}
        for match in matches:
            # logging.debug(f"Match, key='{match.group(1)}', start={match.start(1)}, end={match.end(1)}")
            key = match.group(1)
            value_start = match.end(0)
            value_end = sf_metadata_content.find("\n",value_start) if key != 'info' else end
            # logging.debug(f"value_start={value_start}, value_end={value_end}")
            value = sf_metadata_content[value_start:value_end].rstrip()
            # logging.debug(f"key={key}, value={repr(value)}")
            key = key.replace(' ', "_")
            data[key] = value
        if parse_info_text:
            data['info'] = parse_singlefile_info_text(data['info'])
        if normalize_saved_date:
            data['saved_date'] = parse_js_date_to_iso8601(data['saved_date'])
        return data
    return None
    

def get_file_name_id(file_path):
    p = pathlib.Path(file_path)
    name_id = p.name.split(' ')[0]
    return name_id

def extract_html_metadata(html: str) -> dict:
    """
    從 HTML 字串中提取 metadata，返回 dict。
    包含:
      - title: <title>
      - link
      - meta: 所有 <meta> 標籤的 name/property/charset 對應內容
      - headers: 所有 <h1>~<h6> 按頁面順序存成 list
    """
    soup = BeautifulSoup(html, "lxml")
    metadata = {}

    # 抓取 <title>
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.text.strip()

    # 抓取 <meta> 標籤，集中到 metadata['meta']
    meta_dict = {}
    for meta in soup.find_all('meta'):
        if meta.get('name'):
            meta_dict[meta['name']] = meta.get('content', '')
        elif meta.get('property'):
            meta_dict[meta['property']] = meta.get('content', '')
        elif meta.get('charset'):
            meta_dict['charset'] = meta['charset']
    if meta_dict:
        metadata['meta'] = meta_dict


    # 抓取 <link> 標籤
    # link_tags = []
    # for link in soup.find_all('link'):
    #     link_info = {}
    #     for attr in ['rel', 'href', 'type', 'sizes']:
    #         if link.get(attr):
    #             link_info[attr] = link[attr]
    #             # special case for inline href,
    #             # keep only prefix part but not base64 for record only
    #             # MAY filter out in the future
    #             if attr == 'href' and link_info['href'].startswith("data:"):
    #                 link_info[attr] = link_info[attr].split(';')[0]
    #     if link_info:
    #         link_tags.append(link_info)
    # if link_tags:
    #     metadata['links'] = link_tags

    # 抓取所有 <h1>~<h6> 按頁面順序
    headers = []
    for tag in soup.find_all(['h1','h2','h3','h4','h5','h6']):
        tag_text = tag.get_text(strip=False)
        tag_text = re.sub(r'\s+', ' ', tag_text).strip().rstrip()
        headers.append([tag.name, tag_text])
    if headers:
        metadata['headers'] = headers

    return metadata

from urllib.parse import urljoin, urlparse, parse_qsl, urlunparse, urlencode

def build_selector(tag):
    """
    為 BeautifulSoup tag 建立穩定 selector
    使用 tag + nth-of-type
    """
    parts = []
    current = tag

    while current and current.name not in ("[document]", "html"):
        parent = current.parent
        if not parent:
            break

        # 同類型 sibling 中的位置
        same_type = [
            sib for sib in parent.find_all(current.name, recursive=False)
        ]
        if len(same_type) > 1:
            index = same_type.index(current) + 1
            parts.append(f"{current.name}:nth-of-type({index})")
        else:
            parts.append(current.name)

        current = parent

    return " > ".join(reversed(parts))

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign",
    "utm_term", "utm_content", "fbclid"
}

# SKIP_SCHEMES = ("data:", "javascript:", "mailto:", "tel:", )
KEEP_SCHEMES = ('http', 'https')

def normalize_uri(href: str, base_uri: str, strip_tracking_params: bool = True):
    if not isinstance(href,str):
        raise RuntimeError(f'unexpect href {repr(href)} type {type(href)}')

    resolved = urljoin(base_uri, href)
    parsed = urlparse(resolved)

    query = parsed.query
    if strip_tracking_params and parsed.scheme in ('http', 'https'):
        # strip tracking params
        query = urlencode([
            (k, v) for k, v in parse_qsl(parsed.query)
            if k not in TRACKING_PARAMS
        ])

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        ""
    ))

RESOURCE_RELS = {
    "stylesheet", "icon", "preload", "dns-prefetch",
    "preconnect", "modulepreload"
}

STRUCTURAL_RELS = {"prev", "next", "alternate"}

def normalize_links(links: list, base_uri: str) -> list:
    for link in links:
        link['raw_uri'] = link['uri']
        link['uri'] = normalize_uri(link['uri'], base_uri)
    return links

def classify_link(link: dict) -> str:
    """
    link: {
        uri, tag, rel, selector
    }
    returns: indexable | crawlable | ignorable
    """
    url = link.get("url")
    tag = link.get("tag")
    rel = (link.get("rel") or "").lower()

    if not url:
        return "ignorable"

    scheme = urlparse(url).scheme
    if scheme not in ("http", "https"):
        return "ignorable"

    if tag == "link":
        if rel == "canonical":
            return "indexable"
        if rel in STRUCTURAL_RELS:
            return "crawlable"
        if rel in RESOURCE_RELS:
            return "ignorable"

    if tag == "a":
        return "indexable"

    return "crawlable"

def extract_links(html: str, page_url: str) -> list:
    soup = BeautifulSoup(html, "lxml")

    # <base> support
    base_tag = soup.find("base", href=True)
    base_url = base_tag["href"] if base_tag else page_url

    results = []

    for tag in soup.find_all(["a", "link"], href=True):
        results.append({
            # "normalized_uri": clean,
            "uri": tag['href'],
            "tag": tag.name,
            "rel": tag.get("rel")[0] if tag.get("rel") else None,
            "selector": build_selector(tag)
        })

    return results

def filter_links(links, base_uri, link_uri_name='uri'):
    new_links = []
    parsed_base_uri = urlparse(base_uri)
    for link in links:
        uri = link[link_uri_name]
        parsed_uri = urlparse(uri)
        if parsed_uri.scheme not in KEEP_SCHEMES:
            continue
        elif uri == '':
            continue
        elif uri.startswith("#"):
            continue
        elif link['tag'] == 'link' and link['rel'] in ('stylesheet', 'icon', 'preload'):
            continue
        new_links.append(link)
    return new_links

def collect_links(html: str, page_url: str) -> list:
    links = extract_links(html, page_url)
    links = filter_links(links, page_url)
    links = normalize_links(links, page_url)
    return links
    
def find_canonical_link(links):
    for link in links:
        if link['tag'] == 'link' and link['rel'] == 'canonical':
            return link
    return None

def find_canonical_uri(links, base_uri=None, uri_name='uri'):
    link = find_canonical_link(links)
    return link[uri_name] if link else base_uri

def index_singlefile_html_file(file_path):
    content = get_file_content(file_path)
    sf_metadata = parse_singlefile_html_metadata(content)
    if sf_metadata is None:
        raise RuntimeError("Cannot read singlefile html comment for metadata")
    logging.debug(f'sf_metadata: {sf_metadata}')
    file_name_id = get_file_name_id(file_path)
    text = inscriptis.get_text(content)
    # Don't collect all links include <a> now. 
    # Maybe put into html_metadata for record in future.
    # links = collect_links(content, sf_metadata["url"])
    # canonical_uri = find_canonical_uri(links, sf_metadata["url"])
    html_metadata = extract_html_metadata(content)
    file_path_ = pathlib.Path(file_path).absolute()
    file_dir_path = file_path_.parent.as_posix()
    index = {
        "index_created_datetime": datetime.datetime.now().astimezone().isoformat(),
        "index_updated_datetime": datetime.datetime.now().astimezone().isoformat(),
        "file_created_datetime": sf_metadata['saved_date'],
        "file_updated_datetime": sf_metadata['saved_date'],
        "file_id": file_name_id,
        "file_hash_sha256": get_content_hash_sha256_string(content),
        "file_extension": file_path_.suffix,
        "file_stem": file_path_.stem,
        "file_dir_path": file_dir_path,
        "title": html_metadata['title'],
        "origin_uri": sf_metadata["url"],
        "extra": {
            "html": html_metadata,
            "single_file": sf_metadata
        },
        "text": text,
    }
    return index


def main():
    args = parse_args()
    index = index_singlefile_html_file(file_path=args.file_path)
    f = open("index.jsonc", 'w')
    json.dump(index, f, indent=2)







if __name__ == "__main__":
    main()