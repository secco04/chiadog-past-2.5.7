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
        # Regex für neues 2.5.7 Format
        # Flexibel für verschiedene Formatierungen
        self._regex_new = re.compile(
            r"([0-9:.T-]+)\s+[\d.]+\s+harvester\s+chia\.harvester\.harvester:\s+INFO\s+"
            r"challenge_hash:\s+([0-9a-f]+)\s+\.+([0-9]+)\s+plots\s+were\s+eligible\s+for\s+farming\s*"
            r"(?:challenge)?Found\s+([0-9]+)\s+V1\s+proofs"
            r".*?Time:\s+([0-9.]+)\s+s\.\s+Total\s+([0-9]+)\s+plots",
            re.IGNORECASE
        )
        # Regex für altes Format (Fallback)
        self._regex_old = re.compile(
            r"([0-9:.T-]*)\s+[\d.]+\s+harvester\s+(?:src|chia)\.harvester\.harvester(?:\s?):\s+INFO\s+"
            r"([0-9]+)\s+plots\s+were\s+eligible\s+for\s+farming\s+([0-9a-z.]+)\s+"
            r"Found\s+([0-9]+)\s+proofs\.\s+Time:\s+([0-9.]+)\s+s\.\s+Total\s+([0-9]+)\s+plots"
        )

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        
        # Versuche zuerst das neue 2.5.7 Format zu parsen
        matches_new = self._regex_new.findall(logs)
        
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"Regex new format matches: {len(matches_new)}")
            if matches_new:
                for i, match in enumerate(matches_new):
                    logging.debug(f"Match {i+1}: {match}")
        
        for match in matches_new:
            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    challenge_hash=match[1],
                    eligible_plots_count=int(match[2]),
                    found_proofs_count=int(match[3]),
                    search_time_seconds=float(match[4]),
                    total_plots_count=int(match[5]),
                )
            )
        
        # Fallback auf altes Format falls keine neuen Matches gefunden wurden
        if not matches_new:
            matches_old = self._regex_old.findall(logs)
            
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"Regex old format matches: {len(matches_old)}")
                if matches_old:
                    for i, match in enumerate(matches_old):
                        logging.debug(f"Match {i+1}: {match}")
                else:
                    # Zeige einen Teil der Logs zur Fehlersuche
                    log_sample = logs[:500] if len(logs) > 500 else logs
                    logging.debug(f"No matches found. Log sample: {log_sample}")
            
            for match in matches_old:
                parsed_messages.append(
                    HarvesterActivityMessage(
                        timestamp=dateutil_parser.parse(match[0]),
                        eligible_plots_count=int(match[1]),
                        challenge_hash=match[2],
                        found_proofs_count=int(match[3]),
                        search_time_seconds=float(match[4]),
                        total_plots_count=int(match[5]),
                    )
                )

        return parsed_messages
