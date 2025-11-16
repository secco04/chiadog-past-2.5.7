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
        logging.debug("Enabled parser for harvester activity - eligible plot events.")
        self._regex = re.compile(
            r"([0-9:.]*) harvester (?:src|chia).harvester.harvester(?:\s?): INFO\s*challenge_hash: ([0-9a-z.]*) \.{3}([0-9]+) plots were "
            r"eligible for farming challengeFound ([0-9]+) V1 proofs and ([0-9]+) V2 qualities\. Time: ([0-9.]*) s\. "
            r"Total ([0-9]*) plots"
        )

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    eligible_plots_count=int(match[1]),
                    challenge_hash=match[2],
                    found_proofs_count=int(match[3]) + int(match[4]),
                    search_time_seconds=float(match[5]),
                    total_plots_count=int(match[6]),
                )
            )

        return parsed_messages        :returns: A list of parsed messages - can be empty
        """
        
        # KRITISCH: Schreibe in eine separate Datei
        with open("/tmp/chiadog_parser_debug.txt", "a") as f:
            f.write("="*80 + "\n")
            f.write(f"parse() called at {datetime.now()}\n")
            f.write(f"Logs length: {len(logs)}\n")
            f.write(f"First 500 chars:\n{logs[:500]}\n")
            f.write("="*80 + "\n")

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
