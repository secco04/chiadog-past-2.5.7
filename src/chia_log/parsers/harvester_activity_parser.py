# std
import re
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class HarvesterActivityMessage:
    """Data class for parsed harvester activity messages"""
    timestamp: str
    challenge_hash: str
    eligible_plots: int
    proofs_found: int
    search_time: float
    total_plots: int


class HarvesterActivityParser:
    """Parser for Chia harvester activity log messages.
    Compatible with both old and new log formats.
    """

    def __init__(self):
        # Pattern for old format (2.5.6): "Found 0 proofs. Time: 0.19463 s. Total 982 plots"
        # Pattern for new format (2.5.7): "Found 0 V1 proofs and 0 V2 qualities. Time: 0.01284 s. Total 36 plots"
        self._pattern = re.compile(
            r"([0-9:.]*) harvester (?:src|chia).harvester.harvester(?:\s?): INFO\s*([0-9]+) plots were "
            r"eligible for farming ([0-9a-z.]*)\.\.\. Found (?:([0-9]+) proofs|([0-9]+) V1 proofs and ([0-9]+) V2 qualities)\. Time: ([0-9.]*) s\. "
            r"Total ([0-9]*) plots"
        )


# Vollständige __init__ Funktion zum Kopieren:
"""
def __init__(self):
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
"""

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parse harvester activity messages from log text.
        
        Args:
            logs: Raw log text containing harvester messages
            
        Returns:
            List of parsed HarvesterActivityMessage objects
        """
        messages = []
        
        for match in self._pattern.finditer(logs):
            timestamp = match.group(1)
            eligible_plots = int(match.group(2))
            challenge_hash = match.group(3)
            
            # Handle both old and new format for proofs
            # Old format (2.5.6): group(4) contains proofs count
            # New format (2.5.7): group(5) contains V1 proofs, group(6) contains V2 qualities
            if match.group(4):  # Old format
                proofs_found = int(match.group(4))
            else:  # New format
                v1_proofs = int(match.group(5)) if match.group(5) else 0
                v2_qualities = int(match.group(6)) if match.group(6) else 0
                proofs_found = v1_proofs + v2_qualities
            
            search_time = float(match.group(7))
            total_plots = int(match.group(8))
            
            messages.append(HarvesterActivityMessage(
                timestamp=timestamp,
                challenge_hash=challenge_hash,
                eligible_plots=eligible_plots,
                proofs_found=proofs_found,
                search_time=search_time,
                total_plots=total_plots
            ))
        
        return messages
