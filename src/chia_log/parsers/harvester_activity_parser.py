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
    found_v1_proofs_count: int
    found_v2_qualities_count: int
    search_time_seconds: float
    total_plots_count: int


class HarvesterActivityParser:
    """Parser for Chia 2.5.7 harvester INFO log messages"""

    def __init__(self):
        logging.debug("Enabled parser for harvester activity - eligible plot events.")

        #
        # Unterstützt Format z. B.:
        #
        # 2025-11-16T12:08:59.803 2.5.7 harvester chia.harvester.harvester: INFO     challenge_hash: 21124e0338 ...
        # 0 plots were eligible for farming challengeFound 0 V1 proofs and 0 V2 qualities. Time: 0.01310 s. Total 36 plots
        #
        #

        self._regex = re.compile(
            r"([0-9:\-T\.]+)\s+(?:\d+\.\d+\.\d+\s+)?"
            r"harvester (?:src|chia)\.harvester\.harvester: INFO\s*"
            r"(?:challenge_hash:\s*([0-9a-f]+).*?)?"     # optionaler Hash
            r"([0-9]+)\s+plots were eligible for farming.*?"
            r"Found\s+([0-9]+)\s+V1\s+proofs\s+and\s+([0-9]+)\s+V2\s+qualities\."
            r"\s*Time:\s*([0-9\.]+)\s*s\.\s*Total\s+([0-9]+)\s+plots",
            re.IGNORECASE | re.DOTALL
        )

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        parsed_messages = []

        for match in self._regex.findall(logs):
            timestamp = dateutil_parser.parse(match[0])
            challenge_hash = match[1] if match[1] else ""
            eligible = int(match[2])
            v1_proofs = int(match[3])
            v2_qualities = int(match[4])
            time_s = float(match[5])
            total_plots = int(match[6])

            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=timestamp,
                    eligible_plots_count=eligible,
                    challenge_hash=challenge_hash,
                    found_v1_proofs_count=v1_proofs,
                    found_v2_qualities_count=v2_qualities,
                    search_time_seconds=time_s,
                    total_plots_count=total_plots,
                )
            )

        return parsed_messages
