from .base import BaseParser, ParserError
from .csv_parser import CsvParser
from .docx_parser import DocxParser
from .eml_parser import EmlParser
from .image_parser import ImageParser
from .json_parser import JsonParser
from .markdown_parser import MarkdownParser
from .modelica_parser import ModelicaParser
from .pdf_parser import PdfParser
from .puml_parser import PumlParser
from .text_parser import TextParser
from .xlsx_parser import XlsxParser

ALL_PARSERS: tuple[BaseParser, ...] = (
    PdfParser(),
    DocxParser(),
    XlsxParser(),
    CsvParser(),
    JsonParser(),
    EmlParser(),
    MarkdownParser(),
    TextParser(),
    ModelicaParser(),
    PumlParser(),
    ImageParser(),
)

PARSER_BY_EXTENSION: dict[str, BaseParser] = {
    ext: parser for parser in ALL_PARSERS for ext in parser.extensions
}

__all__ = ["BaseParser", "ParserError", "ALL_PARSERS", "PARSER_BY_EXTENSION"]
