# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class HarvesterActivityMessage:
    """Parsed information from harvester logs"""

    timestamp: datetime
    eligible_plots_count: int
    challenge_hash: str
    found_proofs_count: int
    search_time_seconds: float
    total_plots_count: int


class HarvesterActivityParser:
    """This class can parse info log messages from the chia harvester
    Supports both pre-2.5.7 and 2.5.7+ log formats.
    """

    def __init__(self):
        logging.debug("Enabled parser for harvester activity - eligible plot events.")

        # Alte Form (bis 2.5.6), Beispiel:
        # 2025-11-16T12:21:02.376 2.5.6 harvester chia.harvester.harvester: INFO     5 plots were eligible for farming 98e32143ff... Found 0 proofs. Time: 1.16047 s. Total 982 plots
        self._re_old = re.compile(
            r"([0-9:\-T\.]+)\s+(?:[0-9]+\.[0-9]+\.[0-9]+\s+)?"
            r"harvester (?:src|chia)\.harvester\.harvester: INFO\s*"
            r"([0-9]+)\s+plots were eligible for farming\s+([0-9a-fA-F\.]+)\s+Found\s+([0-9]+)\s+proofs\.\s*"
            r"Time:\s*([0-9\.]+)\s*s\.\s*Total\s+([0-9]+)\s+plots",
            re.IGNORECASE,
        )

        # Neues Form (ab 2.5.7), Beispiel:
        # 2025-11-16T12:15:19.819 2.5.7 harvester chia.harvester.harvester: INFO     challenge_hash: 6bf454e9be ...0 plots were eligible for farming challengeFound 0 V1 proofs and 0 V2 qualities. Time: 0.00532 s. Total 36 plots
        # - optionaler challenge_hash vorangestellt
        # - V1 proofs und V2 qualities -> wir summieren zu found_proofs_count
        self._re_new = re.compile(
            r"([0-9:\-T\.]+)\s+(?:[0-9]+\.[0-9]+\.[0-9]+\s+)?"
            r"harvester (?:src|chia)\.harvester\.harvester: INFO\s*"
            r"(?:challenge_hash:\s*([0-9a-fA-F]+).*?)?"     # optional challenge_hash (Gruppe 2)
            r"([0-9]+)\s+plots were eligible for farming.*?"
            r"Found\s+([0-9]+)\s+V1\s+proofs\s+and\s+([0-9]+)\s+V2\s+qualities\.\s*"
            r"Time:\s*([0-9\.]+)\s*s\.\s*Total\s+([0-9]+)\s+plots",
            re.IGNORECASE | re.DOTALL,
        )

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages: List[HarvesterActivityMessage] = []
        used_spans = []  # avoid duplicate parsing of the same region

        # 1) Erst neue Form (greift über mehrere Zeichen/Zeilen dank DOTALL)
        for m in self._re_new.finditer(logs):
            span = m.span()
            # Überspringen, falls dieser Bereich schon von einem anderen Treffer benutzt wurde
            if any(s <= span[0] < e or s < span[1] <= e for s, e in used_spans):
                continue
            used_spans.append(span)

            ts_str = m.group(1)
            challenge = m.group(2) or ""
            eligible = int(m.group(3))
            v1 = int(m.group(4))
            v2 = int(m.group(5))
            time_s = float(m.group(6))
            total = int(m.group(7))

            # Bereinige challenge (falls unerwünschte Punkte vorhanden sind)
            challenge = challenge.rstrip(".")

            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(ts_str),
                    eligible_plots_count=eligible,
                    challenge_hash=challenge,
                    found_proofs_count=(v1 + v2),
                    search_time_seconds=time_s,
                    total_plots_count=total,
                )
            )

        # 2) Dann alte Form (falls noch nicht erfasst)
        for m in self._re_old.finditer(logs):
            span = m.span()
            if any(s <= span[0] < e or s < span[1] <= e for s, e in used_spans):
                continue
            used_spans.append(span)

            ts_str = m.group(1)
            eligible = int(m.group(2))
            challenge = m.group(3) or ""
            found = int(m.group(4))
            time_s = float(m.group(5))
            total = int(m.group(6))

            # challenge kann '98e32143ff...' enthalten -> trim trailing dots
            challenge = challenge.rstrip(".")

            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(ts_str),
                    eligible_plots_count=eligible,
                    challenge_hash=challenge,
                    found_proofs_count=found,
                    search_time_seconds=time_s,
                    total_plots_count=total,
                )
            )

        return parsed_messages
