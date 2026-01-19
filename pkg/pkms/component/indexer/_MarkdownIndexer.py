from typing import Literal,Optional
from pkms.core.model import FileLocation
from pkms.core.model import FileStamp
from pkms.core.model import IndexedDocument
from pkms.core.component.indexer import (
    Indexer,
    IndexerConfig,
    IndexerRuntime
)
from pkms.core.utility import *

from urllib.parse import urljoin, urlparse, parse_qsl, urlunparse, urlencode
import inscriptis
import datetime
import logging
import os

from pkms.lib.markdown_to_html import (
    MarkdownToHtmlConverter,
    MarkdownToHtmlConverterConfig,
    MarkdownToHtmlConverterRuntime,
)
from bs4 import BeautifulSoup

class MarkdownIndexerConfig(IndexerConfig):
    type: Literal['MarkdownIndexerConfig'] = 'MarkdownIndexerConfig'
    converter: MarkdownToHtmlConverterConfig

class MarkdownIndexerRuntime(IndexerRuntime):
    def __init__(self, *args, config: MarkdownIndexerConfig, **kwargs):
        self.converter = MarkdownToHtmlConverterRuntime(config=config.converter)

class MarkdownIndexer(Indexer):
    Config = MarkdownIndexerConfig
    Runtime = MarkdownIndexerRuntime

    def __init__(self, config: MarkdownIndexerConfig, runtime: Optional[MarkdownIndexerRuntime] = None):
        if runtime is None:
            runtime = MarkdownIndexerRuntime(config=config)
        super().__init__(config=config, runtime=runtime)
        self.converter = MarkdownToHtmlConverter(config=config.converter, runtime=runtime.converter)

    def index(self, file_location: FileLocation, file_stamp: FileStamp) -> IndexedDocument:
        assert file_location.scheme == 'file'
        assert file_location.authority == ''
        assert os.path.isabs(file_location.path)
        # NOTE: MAYBE support relative path in future, now enforce absoulte path
        # TODO: expose title in the converter
        content = self.converter.convert(file_location.path, title=None)
        soup = BeautifulSoup(content, "lxml")
        title = soup.title.text
        text = inscriptis.get_text(content)
        now = datetime.datetime.now()
        index = IndexedDocument(**{
            "index_created_datetime": now.astimezone().isoformat(),
            "index_updated_datetime": now.astimezone().isoformat(),
            "file_created_datetime": file_stamp.created_datetime,
            "file_modified_datetime": file_stamp.modified_datetime,
            "file_id": file_stamp.id,
            "file_uid": file_stamp.uid,
            "file_uri": file_location.uri,
            "file_hash_sha256": file_stamp.hash_sha256,
            "file_size": file_stamp.size,
            "file_extension": file_stamp.extension,
            "file_kind": file_stamp.kind,
            # Select a good title, fallback if needed
            "title": title if title else file_stamp.title,
            "importance": file_stamp.importance,
            "origin_uri": None,
            "text": text,
            "extra": {},
        })
        return index