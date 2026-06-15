"""
Blockchain Audit Anchoring — Merkle tree hashing of audit entries.
Provides mathematical proof that the audit trail has not been tampered with.
"""

import hashlib
from datetime import datetime


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def compute_merkle_root(entries: list[dict]) -> str:
    """Compute the Merkle root hash of a list of audit entries."""
    if not entries:
        return _sha256("empty-block")

    # Hash each entry
    hashes = [
        _sha256(f"{e.get('id','')}{e.get('cin_accessed','')}{e.get('accessed_by','')}"
                f"{e.get('purpose','')}{e.get('timestamp','')}")
        for e in entries
    ]

    # Build Merkle tree
    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])  # duplicate last
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = _sha256(hashes[i] + hashes[i + 1])
            next_level.append(combined)
        hashes = next_level

    return hashes[0]


def create_anchor(entries: list[dict], block_number: int) -> dict:
    """Create a blockchain anchor record."""
    merkle = compute_merkle_root(entries)
    now = datetime.utcnow()

    # Simulated blockchain transaction
    prev_hash = _sha256(f"block-{block_number - 1}") if block_number > 0 else "0" * 64
    block_hash = _sha256(f"{prev_hash}{merkle}{now.isoformat()}{block_number}")

    return {
        "block_number": block_number,
        "merkle_root": merkle,
        "previous_hash": prev_hash,
        "block_hash": block_hash,
        "entries_count": len(entries),
        "timestamp": now.isoformat(),
        "entry_ids": [str(e.get("id", "")) for e in entries],
    }


def verify_entries(entries: list[dict], expected_merkle: str) -> bool:
    """Verify that entries match the expected Merkle root."""
    return compute_merkle_root(entries) == expected_merkle
