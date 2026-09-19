"""EML parser. Mirrors `Document Agent.md`, Section 14.

Reconstructs the email thread: the top-level message is parsed with the
stdlib `email` module, and inline quoted replies (`-----Original
Message-----` blocks, the common plain-text quoting convention used by the
golden datasets) are split out into their own observations so each reply
keeps its own sender/date/subject and its position in the thread. Email
ordering matters — a later message can supersede an earlier decision.
"""

from __future__ import annotations

import re
from email import message_from_bytes
from email.message import Message
from pathlib import Path

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError

_QUOTE_SPLIT = re.compile(r"\n-{3,}\s*Original Message\s*-{3,}\n", re.IGNORECASE)
_HEADER_LINE = re.compile(r"^(From|Date|Subject|To)\s*:\s*(.*)$", re.IGNORECASE | re.MULTILINE)


def _body_text(msg: Message) -> str:
    if msg.is_multipart():
        parts = [_body_text(part) for part in msg.walk() if not part.is_multipart()]
        return "\n".join(p for p in parts if p)
    payload = msg.get_payload(decode=True)
    if payload is None:
        return str(msg.get_payload())
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def _split_thread(body: str) -> list[str]:
    return [chunk.strip() for chunk in _QUOTE_SPLIT.split(body) if chunk.strip()]


def _extract_headers(chunk: str) -> dict[str, str]:
    return {m.group(1).lower(): m.group(2).strip() for m in _HEADER_LINE.finditer(chunk)}


class EmlParser(BaseParser):
    parser_name = "eml_parser"
    extensions = (".eml",)

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            msg = message_from_bytes(file_path.read_bytes())
        except Exception as exc:
            raise ParserError(f"Unable to parse EML: {exc}") from exc

        body = _body_text(msg)
        chunks = _split_thread(body)
        if not chunks:
            raise ParserError("EML body was empty after parsing.")

        observations: list[Observation] = []

        # First chunk uses the top-level MIME headers; later chunks parse their own inline headers.
        top_from = msg.get("From", "")
        top_date = msg.get("Date", "")
        top_subject = msg.get("Subject", "")
        headers = _extract_headers(chunks[0])
        content = (
            f"From: {headers.get('from', top_from)}\n"
            f"Date: {headers.get('date', top_date)}\n"
            f"Subject: {headers.get('subject', top_subject)}\n\n{chunks[0]}"
        )
        observations.append(
            Observation(
                observation_id=self.next_observation_id(document),
                document_id=document.document_id,
                type=ObservationType.EMAIL_MESSAGE,
                content=content,
                location=SourceLocation(section="message 1 (most recent)"),
                parser=self.parser_name,
                parser_version=self.parser_version,
            )
        )

        for position, chunk in enumerate(chunks[1:], start=2):
            headers = _extract_headers(chunk)
            content = (
                f"From: {headers.get('from', '')}\n"
                f"Date: {headers.get('date', '')}\n"
                f"Subject: {headers.get('subject', '')}\n\n{chunk}"
            )
            observations.append(
                Observation(
                    observation_id=self.next_observation_id(document),
                    document_id=document.document_id,
                    type=ObservationType.EMAIL_MESSAGE,
                    content=content,
                    location=SourceLocation(section=f"message {position} (quoted reply)"),
                    parser=self.parser_name,
                    parser_version=self.parser_version,
                )
            )

        return observations
