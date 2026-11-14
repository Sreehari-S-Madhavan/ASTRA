"""
ASTRA Medical Protocols Registry
Defines the clinical aerospace emergency procedures, actions, and escalation criteria.
"""
from typing import Dict, Any, List, Optional
from astra.database.db_manager import db_manager


class MedicalProtocolsRegistry:
    """Provides fast access to validated clinical aerospace emergency protocols."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_all_protocols(self) -> List[Dict[str, Any]]:
        """Fetch all protocols from the database."""
        rows = db_manager.execute_query("SELECT * FROM medical_protocols ORDER BY code ASC")
        self._cache = {row["id"]: row for row in rows}
        return rows

    def get_protocol_by_id(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        if protocol_id in self._cache:
            return self._cache[protocol_id]
        row = db_manager.execute_single("SELECT * FROM medical_protocols WHERE id = ?", (protocol_id,))
        if row:
            self._cache[protocol_id] = row
        return row

    def get_protocol_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return db_manager.execute_single("SELECT * FROM medical_protocols WHERE code = ?", (code,))


protocol_registry = MedicalProtocolsRegistry()
