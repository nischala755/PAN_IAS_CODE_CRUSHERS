from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

try:
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover
    fuzz = None

CORP_SUFFIXES = [
    "private limited",
    "pvt ltd",
    "pvt. ltd",
    "pvt ltd.",
    "pvt. ltd.",
    "ltd",
    "limited",
]
OLD_RECORD_YEAR = 2021


@dataclass
class GroupResult:
    ubid: str
    status: str
    records: List[Dict]


def _clean(value: Optional[str]) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_name(name: Optional[str]) -> str:
    cleaned = _clean(name).lower()
    cleaned = " ".join(cleaned.split())
    for suffix in CORP_SUFFIXES:
        cleaned = cleaned.replace(suffix, "")
    cleaned = " ".join(cleaned.split())
    return cleaned


def name_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if fuzz is not None:
        return float(fuzz.ratio(a, b))
    return SequenceMatcher(None, a, b).ratio() * 100.0


def load_and_normalize(csv_paths: List[Path]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for path in csv_paths:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df["source"] = path.stem
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    for col in ["name", "address", "pincode", "pan", "phone"]:
        combined[col] = combined[col].fillna("").astype(str).str.strip()

    if "record_year" not in combined.columns:
        combined["record_year"] = pd.Timestamp.now().year
    combined["record_year"] = pd.to_numeric(combined["record_year"], errors="coerce").fillna(pd.Timestamp.now().year).astype(int)

    combined["name_norm"] = combined["name"].apply(normalize_name)
    combined["pincode_norm"] = combined["pincode"].str.replace(r"\D", "", regex=True)
    combined["pan_norm"] = combined["pan"].str.upper()
    combined["phone_norm"] = combined["phone"].str.replace(r"\D", "", regex=True)
    return combined


def is_same_business(a: pd.Series, b: pd.Series, threshold: float = 85.0) -> bool:
    if a["pan_norm"] and b["pan_norm"] and a["pan_norm"] == b["pan_norm"]:
        return True

    if a["pincode_norm"] != b["pincode_norm"]:
        return False

    score = name_similarity(a["name_norm"], b["name_norm"])
    return score >= threshold


def _assign_ubid(group_df: pd.DataFrame, int_counter: int) -> str:
    pans = [p for p in group_df["pan_norm"].tolist() if p]
    if pans:
        return f"KA-PAN-{pans[0]}"
    return f"KA-INT-{int_counter:04d}"


def _group_status(group_df: pd.DataFrame) -> str:
    has_phone = group_df["phone_norm"].astype(bool).any()
    if has_phone:
        return "ACTIVE"

    oldest_year = int(group_df["record_year"].min())
    if oldest_year <= OLD_RECORD_YEAR:
        return "INACTIVE"

    return "ACTIVE"


def build_groups(df: pd.DataFrame, threshold: float = 85.0) -> List[GroupResult]:
    groups: List[List[int]] = []

    for idx in df.index:
        row = df.loc[idx]
        placed = False
        for group in groups:
            for member_idx in group:
                if is_same_business(row, df.loc[member_idx], threshold=threshold):
                    group.append(idx)
                    placed = True
                    break
            if placed:
                break

        if not placed:
            groups.append([idx])

    results: List[GroupResult] = []
    int_counter = 1
    for group in groups:
        group_df = df.loc[group].copy()
        ubid = _assign_ubid(group_df, int_counter)
        if ubid.startswith("KA-INT"):
            int_counter += 1

        status = _group_status(group_df)
        records = group_df[
            ["source", "name", "address", "pincode", "pan", "phone", "record_year", "name_norm"]
        ].to_dict(orient="records")
        results.append(GroupResult(ubid=ubid, status=status, records=records))

    return results


def build_snapshot(data_dir: Path, threshold: float = 85.0) -> Dict:
    csv_paths = [
        data_dir / "shop.csv",
        data_dir / "factories.csv",
        data_dir / "labour.csv",
    ]
    df = load_and_normalize(csv_paths)
    groups = build_groups(df, threshold=threshold)

    return {
        "total_records": int(len(df)),
        "unique_businesses": int(len(groups)),
        "groups": [
            {
                "ubid": g.ubid,
                "status": g.status,
                "records": g.records,
            }
            for g in groups
        ],
    }
