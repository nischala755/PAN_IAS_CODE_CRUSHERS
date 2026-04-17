from pathlib import Path

from ubid_mesh import build_snapshot


def print_demo(snapshot: dict) -> None:
    print("\nUBID Mesh Demo")
    print("=" * 60)
    print(f"Total records: {snapshot['total_records']}")
    print(f"Unique businesses (UBIDs): {snapshot['unique_businesses']}")

    for group in snapshot["groups"]:
        print("\n" + "-" * 60)
        print(f"UBID: {group['ubid']} | STATUS: {group['status']}")
        for rec in group["records"]:
            print(
                f"  - [{rec['source']}] {rec['name']} | {rec['address']} | "
                f"PIN: {rec['pincode']} | PAN: {rec['pan'] or '-'} | PHONE: {rec['phone'] or '-'}"
            )


def main() -> None:
    snapshot = build_snapshot(Path("data"))
    print_demo(snapshot)


if __name__ == "__main__":
    main()
