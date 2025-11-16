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

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.info("="*50)
        logging.info("Harvester Activity Parser - Version 2.5.7")
        logging.info("="*50)
        
        # Regex für Chia 2.5.7 Format
        # 2025-11-16T17:40:06.742 2.5.7 harvester chia.harvester.harvester: INFO     challenge_hash: 37fe940f6b ...0 plots were eligible for farming challengeFound 0 V1 proofs and 0 V2 qualities. Time: 0.00523 s. Total 36 plots
        self._regex_new = re.compile(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})\s+"  # Timestamp
            r"[\d.]+\s+"  # Version
            r"harvester\s+"  # harvester
            r"chia\.harvester\.harvester:\s+"  # module
            r"INFO\s+"  # log level
            r"challenge_hash:\s+([0-9a-f]+)\s+"  # challenge hash
            r"\.\.\.(\d+)\s+"  # eligible plots
            r"plots\s+were\s+eligible\s+for\s+farming\s+"
            r"challengeFound\s+(\d+)\s+V1\s+proofs"  # proofs found
            r".*?"  # ignore V2 qualities
            r"Time:\s+([\d.]+)\s+s\.\s+"  # time
            r"Total\s+(\d+)\s+plots"  # total plots
        )
        
        # Regex für alte Chia Versionen (Fallback)
        self._regex_old = re.compile(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})\s+"
            r"[\d.]+\s+harvester\s+(?:src|chia)\.harvester\.harvester(?:\s?):\s+INFO\s+"
            r"(\d+)\s+plots\s+were\s+eligible\s+for\s+farming\s+([0-9a-z.]+)\s+"
            r"Found\s+(\d+)\s+proofs\.\s+Time:\s+([\d.]+)\s+s\.\s+Total\s+(\d+)\s+plots"
        )
        
        logging.info("Parser initialized for Chia 2.5.7 and older versions")

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        
        # Versuche neues 2.5.7 Format
        matches_new = self._regex_new.findall(logs)
        
        for match in matches_new:
            try:
                msg = HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    challenge_hash=match[1],
                    eligible_plots_count=int(match[2]),
                    found_proofs_count=int(match[3]),
                    search_time_seconds=float(match[4]),
                    total_plots_count=int(match[5]),
                )
                parsed_messages.append(msg)
                logging.debug(f"Parsed 2.5.7: {match[2]} eligible, {match[5]} total, {match[4]}s")
            except Exception as e:
                logging.error(f"Error parsing new format: {e}, match: {match}")
        
        # Fallback auf altes Format
        if not matches_new:
            matches_old = self._regex_old.findall(logs)
            
            for match in matches_old:
                try:
                    msg = HarvesterActivityMessage(
                        timestamp=dateutil_parser.parse(match[0]),
                        eligible_plots_count=int(match[1]),
                        challenge_hash=match[2],
                        found_proofs_count=int(match[3]),
                        search_time_seconds=float(match[4]),
                        total_plots_count=int(match[5]),
                    )
                    parsed_messages.append(msg)
                    logging.debug(f"Parsed old format: {match[1]} eligible, {match[5]} total")
                except Exception as e:
                    logging.error(f"Error parsing old format: {e}, match: {match}")

        return parsed_messages
