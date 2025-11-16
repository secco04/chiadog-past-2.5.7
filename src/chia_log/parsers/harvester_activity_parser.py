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
    
    # Pattern for old format: "Found 0 proofs. Time: 0.01783 s. Total 54 plots"
    # Pattern for new format: "Found 0 V1 proofs and 0 V2 qualities. Time: 0.01284 s. Total 36 plots"
        self._pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}).*?'
            r'challenge_hash:\s*(\w+).*?'
            r'(\d+)\s+plots?\s+were\s+eligible.*?'
            r'Found\s+(?:(\d+)\s+(?:V1\s+)?proofs?(?:\s+and\s+\d+\s+V2\s+qualities)?|(\d+)\s+V1\s+proofs\s+and\s+(\d+)\s+V2\s+qualities).*?'
            r'Time:\s+([\d.]+)\s+s.*?'
            r'Total\s+(\d+)\s+plots',
            re.DOTALL
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
                    found_proofs_count=int(match[3]),
                    search_time_seconds=float(match[4]),
                    total_plots_count=int(match[5]),
                )
            )
        logging.debug(parsed_messages) 
        return parsed_messages
