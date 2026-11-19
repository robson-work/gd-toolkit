#!/usr/bin/env python3
"""Balance workbook helper for the gd /balance command.

The workbook is the shared balancing database between the AI and the game
designer (GD). This script is the only way the AI writes to it, so that:
  * manual GD edits are detected (diff against a hidden _snapshot sheet),
    logged as GD changes, and never overwritten without approval;
  * every change lands in the Changelog with who, why, old and new value;
  * the Sync sheet records which approved values are in the game code.

Commands (all print JSON on stdout; messages on stderr):
  init  BOOK [--game NAME]          create a new workbook
  dump  BOOK [--sheet S]            values + formulas of tracked sheets
  diff  BOOK                        manual edits since the last AI write
  ack   BOOK [--reason TEXT]        log pending edits as GD changes, re-snapshot
  owners BOOK                       cells whose last change was made by the GD
  apply BOOK CHANGES.json           AI writes (refuses GD-owned cells unless approved)
  link  BOOK LINKS.json             map cells to code locations in Sync
  sync-status BOOK                  in_sync / pending / missing per Sync row
  mark-synced BOOK [KEY ...|--all]  record that values now match the code

CHANGES.json: [{"sheet","id","field","value","reason","approved"?}]
  value: number, string, bool, null, or a formula string starting with "=".
  In formulas write {field} for a cell in the same row and {Sheet:id:field}
  for any other cell; the script turns them into A1 references, so never
  write column letters by hand. Example: "={damage}/{fire_rate_s}".
LINKS.json:   [{"sheet","id","field","code_ref"}]
KEY:          sheet/id/field

Exit codes: 0 ok, 2 usage, 3 unacknowledged GD edits, 4 GD-owned cell
without approval, 5 workbook open in Excel, 6 workbook holds content this
script would destroy on save (charts, images, pivots, macros), 7 bad data.
"""
import argparse
import datetime as dt
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:  # pragma: no cover
    sys.exit("openpyxl is missing: run this script through run.sh")

README, TARGETS, BENCHMARKS, CHANGELOG, SYNC, SNAPSHOT = (
    "README", "Targets", "Benchmarks", "Changelog", "Sync", "_snapshot")
UNTRACKED = {README, CHANGELOG, SYNC}
CHANGELOG_COLS = ["when", "by", "sheet", "id", "field", "old", "new", "reason", "status"]
SYNC_COLS = ["sheet", "id", "field", "code_ref", "last_synced_value", "synced_at"]
SNAPSHOT_COLS = ["sheet", "id", "field", "value"]
TARGET_COLS = ["id", "metric", "target", "min", "max", "actual", "source", "status", "notes"]
BENCHMARK_COLS = ["id", "game", "system", "metric", "value", "unit", "context", "source_url", "accessed",
                  "confidence", "notes"]
LOSSY_PARTS = ("xl/charts/", "xl/drawings/", "xl/pivotTables/", "xl/pivotCache/", "xl/media/", "xl/vbaProject.bin")
BLUE, BLACK = Font(color="0000FF"), Font(color="000000")
HEADER_FONT, HEADER_FILL = Font(bold=True), PatternFill("solid", fgColor="EDEDED")
HISTORY_KEEP = 30

README_LINES = [
    "Balance workbook — shared between the game designer (GD) and the AI (/gd:balance).",
    "",
    "How to edit",
    "• Blue cells are input values: change them freely.",
    "• Black cells are formulas (derived values). Edit them only on purpose.",
    "• Every data sheet has an 'id' column. Never rename an id; add rows and columns freely.",
    "• Sheets whose name starts with '_' are bookkeeping. Don't edit them.",
    "• Close the workbook in Excel before running /gd:balance, so your edits are saved.",
    "",
    "What the AI does with your edits",
    "• Each run starts by detecting what you changed and logging it in Changelog as by=GD.",
    "• A value you changed is yours: the AI never overwrites it without your approval.",
    "",
    "Sheets",
    "• Targets: balance goals with tolerances; 'source' says Observed (our live data), Benchmark (competitors),",
    "  Measured (test/sim) or Estimated (model).",
    "• Benchmarks: competitor and reference-game numbers, one per row, each with its source link and date.",
    "• Changelog: every change, who made it (AI or GD), why, and its status.",
    "• Sync: which code location or remote-config field each value maps to, and the last value synced to the game.",
    "",
    "Keep charts, images and pivot tables in a separate workbook: this one is rewritten by a script that can't preserve them.",
]


def out(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def now() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def norm(value) -> str:
    """Canonical string for a cell value; formulas keep their text."""
    if value is None:
        return ""
    if hasattr(value, "text") and not isinstance(value, str):  # ArrayFormula
        return str(value.text)
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    return repr(value) if isinstance(value, float) else str(value)


def die(code: int, msg: str, **extra) -> None:
    print(msg, file=sys.stderr)
    if extra:
        out(extra)
    sys.exit(code)


# ---------------------------------------------------------------- reading

def tracked_sheets(wb):
    return [ws for ws in wb.worksheets if ws.title not in UNTRACKED and not ws.title.startswith("_")]


def header_map(ws):
    """{field: column_index}, id column index (or None)."""
    fields, id_col = {}, None
    for cell in ws[1]:
        name = norm(cell.value).strip()
        if not name:
            continue
        if name.lower() == "id" and id_col is None:
            id_col = cell.column
        else:
            fields[name] = cell.column
    return fields, id_col


def read_sheet(ws, problems):
    """{(id, field): value} plus a {id: row} index."""
    fields, id_col = header_map(ws)
    cells, rows = {}, {}
    if id_col is None:
        if ws.max_row > 1 or fields:
            problems.append(f"{ws.title}: no 'id' column in row 1, sheet is not tracked")
        return cells, rows, fields
    for r in range(2, ws.max_row + 1):
        rid = norm(ws.cell(r, id_col).value).strip()
        values = {f: ws.cell(r, c).value for f, c in fields.items()}
        if not rid:
            if any(v is not None for v in values.values()):
                problems.append(f"{ws.title}!row {r}: has values but no id, not tracked")
            continue
        if rid in rows:
            problems.append(f"{ws.title}: duplicate id '{rid}' (rows {rows[rid]} and {r}), later row ignored")
            continue
        rows[rid] = r
        for f, v in values.items():
            cells[(rid, f)] = norm(v)
    return cells, rows, fields


def read_tracked(wb):
    problems, state = [], {}
    for ws in tracked_sheets(wb):
        cells, _, _ = read_sheet(ws, problems)
        for (rid, f), v in cells.items():
            state[(ws.title, rid, f)] = v
    return state, problems


def read_snapshot(wb):
    if SNAPSHOT not in wb.sheetnames:
        return None
    ws, snap = wb[SNAPSHOT], {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row and row[0] is not None:
            snap[(norm(row[0]), norm(row[1]), norm(row[2]))] = norm(row[3])
    return snap


def compute_diff(wb):
    state, problems = read_tracked(wb)
    snap = read_snapshot(wb)
    if snap is None:
        die(7, f"no {SNAPSHOT} sheet: this workbook was not created by /gd:balance (use init, or import it by hand)")
    changes = []
    for key in sorted(set(state) | set(snap)):
        old, new = snap.get(key), state.get(key)
        if old == new or (old in (None, "") and new in (None, "")):
            continue
        kind = "added" if old is None else "removed" if new is None else "changed"
        changes.append({"sheet": key[0], "id": key[1], "field": key[2], "old": old, "new": new, "kind": kind})
    return changes, problems, state


def read_owners(wb):
    owners = {}
    if CHANGELOG not in wb.sheetnames:
        return owners
    for row in wb[CHANGELOG].iter_rows(min_row=2, values_only=True):
        if not row or row[2] is None:
            continue
        rec = dict(zip(CHANGELOG_COLS, row))
        if rec.get("status") in ("applied", "synced"):
            owners[(norm(rec["sheet"]), norm(rec["id"]), norm(rec["field"]))] = norm(rec["by"])
    return owners


# ---------------------------------------------------------------- writing

def load(book: Path):
    if not book.is_file():
        die(2, f"workbook not found: {book}")
    return openpyxl.load_workbook(book)


def guard_write(book: Path) -> None:
    lock = book.with_name("~$" + book.name)
    if lock.exists():
        die(5, f"{book.name} is open in Excel ({lock.name} exists). Ask the GD to save and close it, then retry.")
    with zipfile.ZipFile(book) as z:
        lossy = sorted({p for n in z.namelist() for p in LOSSY_PARTS if n.startswith(p)})
    if lossy:
        die(6, f"{book.name} contains parts that would be lost on save: {', '.join(lossy)}. "
               "Move charts/images/pivots to a separate workbook, then retry.", parts=lossy)


def backup(book: Path) -> Path:
    hist = book.parent / ".history"
    hist.mkdir(exist_ok=True)
    dest = hist / f"{book.stem}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')}{book.suffix}"
    shutil.copy2(book, dest)
    olds = sorted(hist.glob(f"{book.stem}-*{book.suffix}"))
    for old in olds[:-HISTORY_KEEP]:
        old.unlink()
    return dest


def save(wb, book: Path) -> None:
    wb.calculation.fullCalcOnLoad = True  # Excel/Numbers recompute formulas on open
    tmp = book.with_name(f".{book.stem}.tmp{book.suffix}")
    wb.save(tmp)
    tmp.replace(book)


def style_header(ws) -> None:
    for cell in ws[1]:
        cell.font, cell.fill = HEADER_FONT, HEADER_FILL
    ws.freeze_panes = "B2" if norm(ws.cell(1, 1).value).lower() == "id" else "A2"


def new_table(wb, title, cols, index=None):
    ws = wb.create_sheet(title, index) if index is not None else wb.create_sheet(title)
    ws.append(cols)
    style_header(ws)
    return ws


def write_snapshot(wb) -> None:
    state, _ = read_tracked(wb)
    if SNAPSHOT in wb.sheetnames:
        del wb[SNAPSHOT]
    ws = wb.create_sheet(SNAPSHOT)
    ws.append(SNAPSHOT_COLS)
    for (s, rid, f), v in sorted(state.items()):
        ws.append([s, rid, f, v])
    ws.sheet_state = "hidden"


def log(wb, by, sheet, rid, field, old, new, reason, status="applied") -> None:
    wb[CHANGELOG].append([now(), by, sheet, rid, field, old, new, reason, status])


PLACEHOLDER = re.compile(r"\{([A-Za-z_][\w ]*?)(?::([^{}:]+):([^{}:]+))?\}")


def locate(wb, sheet, rid, field):
    """Absolute A1 reference of sheet/id/field, or None."""
    if sheet not in wb.sheetnames:
        return None
    ws = wb[sheet]
    fields, _ = header_map(ws)
    _, rows, _ = read_sheet(ws, [])
    if field not in fields or rid not in rows:
        return None
    return f"{get_column_letter(fields[field])}{rows[rid]}"


def resolve_formula(wb, ws, rid, formula):
    """Replace {field} (same row) and {Sheet:id:field} with cell references.

    Braces that match neither form (e.g. Excel array constants) are left alone.
    """
    missing = []

    def repl(m):
        if m.group(2) is None:
            ref = locate(wb, ws.title, rid, m.group(1))
            if ref is None and m.group(1) in header_map(ws)[0]:
                missing.append(m.group(0))
            return ref or m.group(0)
        sheet, oid, field = m.group(1), m.group(2), m.group(3)
        ref = locate(wb, sheet, oid, field)
        if ref is None:
            missing.append(m.group(0))
            return m.group(0)
        return f"'{sheet}'!${ref[0:len(ref.rstrip('0123456789'))]}${ref[len(ref.rstrip('0123456789')):]}"

    out_f = PLACEHOLDER.sub(repl, formula)
    if missing:
        die(7, f"{ws.title}/{rid}: formula placeholders not found: {', '.join(missing)}")
    return out_f


def set_cell(ws, rid, field, value):
    """Write one value, creating the column/row if needed. Returns old value."""
    fields, id_col = header_map(ws)
    if id_col is None:
        die(7, f"sheet {ws.title} has no 'id' column")
    if field not in fields:
        col = ws.max_column + 1 if ws.max_column >= 1 and ws.cell(1, 1).value is not None else 2
        ws.cell(1, col, field)
        style_header(ws)
        fields[field] = col
    _, rows, _ = read_sheet(ws, [])
    if rid not in rows:
        r = ws.max_row + 1
        ws.cell(r, id_col, rid)
        rows[rid] = r
    cell = ws.cell(rows[rid], fields[field])
    old = norm(cell.value)
    cell.value = value
    cell.font = BLACK if isinstance(value, str) and value.startswith("=") else BLUE
    return old


# ---------------------------------------------------------------- commands

def cmd_init(a):
    book = Path(a.book)
    if book.exists():
        die(2, f"{book} already exists")
    book.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = README
    ws.append([f"{a.game} — balance workbook" if a.game else "Balance workbook"])
    ws["A1"].font = Font(bold=True, size=14)
    for line in README_LINES:
        ws.append([line])
    ws.column_dimensions["A"].width = 110
    new_table(wb, TARGETS, TARGET_COLS)
    new_table(wb, BENCHMARKS, BENCHMARK_COLS)
    new_table(wb, CHANGELOG, CHANGELOG_COLS)
    new_table(wb, SYNC, SYNC_COLS)
    write_snapshot(wb)
    log(wb, "AI", "", "", "", "", "", "workbook created", "applied")
    save(wb, book)
    out({"created": str(book)})


def cmd_dump(a):
    book = Path(a.book)
    wb_f, wb_v = load(book), openpyxl.load_workbook(book, data_only=True)
    problems, result, stale = [], {}, False
    for ws in tracked_sheets(wb_f):
        if a.sheet and ws.title != a.sheet:
            continue
        cells, rows, fields = read_sheet(ws, problems)
        wv = wb_v[ws.title]
        sheet = {"fields": list(fields), "rows": {}}
        for rid, r in rows.items():
            row = {}
            for f, c in fields.items():
                raw = cells[(rid, f)]
                if raw.startswith("="):
                    cached = wv.cell(r, c).value
                    stale |= cached is None
                    row[f] = {"f": raw, "v": cached}
                else:
                    row[f] = ws.cell(r, c).value
            sheet["rows"][rid] = row
        result[ws.title] = sheet
    out({"sheets": result, "problems": problems,
         "formulas_stale": stale,
         "note": "formula 'v' is Excel's cached result; null means not recalculated since the last script write"
         if stale else None})


def cmd_diff(a):
    changes, problems, _ = compute_diff(load(Path(a.book)))
    out({"pending_gd_edits": changes, "problems": problems})


def cmd_ack(a):
    book = Path(a.book)
    wb = load(book)
    changes, problems, _ = compute_diff(wb)
    if not changes:
        out({"acknowledged": [], "problems": problems})
        return
    guard_write(book)
    backup(book)
    for c in changes:
        log(wb, "GD", c["sheet"], c["id"], c["field"], c["old"], c["new"], a.reason or "manual edit in Excel")
    write_snapshot(wb)
    save(wb, book)
    out({"acknowledged": changes, "problems": problems})


def cmd_owners(a):
    owners = read_owners(load(Path(a.book)))
    out([{"sheet": s, "id": i, "field": f} for (s, i, f), by in sorted(owners.items()) if by == "GD"])


def cmd_apply(a):
    book = Path(a.book)
    try:
        changes = json.loads(Path(a.changes).read_text(encoding="utf-8"))
        assert isinstance(changes, list)
    except (OSError, ValueError, AssertionError) as e:
        die(2, f"bad changes file: {e}")
    wb = load(book)
    pending, _, _ = compute_diff(wb)
    if pending:
        die(3, "the GD has unacknowledged edits: run `ack` first and review them", pending_gd_edits=pending)
    owners = read_owners(wb)
    blocked, bad = [], []
    for c in changes:
        if not all(c.get(k) not in (None, "") for k in ("sheet", "id", "field", "reason")) or "value" not in c:
            bad.append(c)
        elif c["sheet"] in UNTRACKED or c["sheet"].startswith("_"):
            bad.append({**c, "error": "reserved sheet"})
        elif owners.get((c["sheet"], str(c["id"]), c["field"])) == "GD" and not c.get("approved"):
            blocked.append(c)
    if bad:
        die(7, "invalid changes (need sheet, id, field, value, reason; no reserved sheets)", invalid=bad)
    if blocked:
        die(4, "these cells were last set by the GD; ask for approval and resend with \"approved\": true",
            blocked=blocked)
    guard_write(book)
    backup(book)
    applied = []
    is_formula = lambda c: isinstance(c["value"], str) and c["value"].startswith("=")
    # Plain values first, so formula placeholders can point at cells created in this batch.
    for c in sorted(changes, key=is_formula):
        # New data sheets go before Changelog, so they sit together after Targets.
        ws = wb[c["sheet"]] if c["sheet"] in wb.sheetnames else new_table(
            wb, c["sheet"], ["id"], index=wb.sheetnames.index(CHANGELOG) if CHANGELOG in wb.sheetnames else None)
        if is_formula(c):
            set_cell(ws, str(c["id"]), c["field"], None)  # make sure the target column/row exists
            c = {**c, "value": resolve_formula(wb, ws, str(c["id"]), c["value"])}
        old = set_cell(ws, str(c["id"]), c["field"], c["value"])
        new = norm(c["value"])
        if old == new:
            continue
        reason = c["reason"] + (" (approved by GD)" if c.get("approved") else "")
        log(wb, "AI", c["sheet"], str(c["id"]), c["field"], old, new, reason)
        applied.append({"sheet": c["sheet"], "id": str(c["id"]), "field": c["field"], "old": old, "new": new})
    write_snapshot(wb)
    save(wb, book)
    out({"applied": applied})


def sync_rows(wb):
    ws = wb[SYNC]
    for r in range(2, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, len(SYNC_COLS) + 1)]
        if vals[0] is not None:
            yield r, dict(zip(SYNC_COLS, vals))


def cmd_link(a):
    book = Path(a.book)
    links = json.loads(Path(a.links).read_text(encoding="utf-8"))
    wb = load(book)
    guard_write(book)
    ws, existing = wb[SYNC], {}
    for r, row in sync_rows(wb):
        existing[(norm(row["sheet"]), norm(row["id"]), norm(row["field"]))] = r
    for ln in links:
        key = (ln["sheet"], str(ln["id"]), ln["field"])
        if key in existing:
            ws.cell(existing[key], 4, ln["code_ref"])
        else:
            ws.append([*key, ln["code_ref"], None, None])
    backup(book)
    save(wb, book)
    out({"linked": len(links)})


def cmd_sync_status(a):
    wb = load(Path(a.book))
    state, _ = read_tracked(wb)
    rows = []
    for _, row in sync_rows(wb):
        key = (norm(row["sheet"]), norm(row["id"]), norm(row["field"]))
        cur = state.get(key)
        last = None if row["last_synced_value"] is None else norm(row["last_synced_value"])
        status = "missing" if cur is None else "in_sync" if cur == last else "pending"
        rows.append({"key": "/".join(key), "code_ref": row["code_ref"], "workbook": cur,
                     "last_synced": last, "synced_at": row["synced_at"], "status": status})
    out(rows)


def cmd_mark_synced(a):
    book = Path(a.book)
    wb = load(book)
    guard_write(book)
    state, _ = read_tracked(wb)
    wanted = None if a.all else {tuple(k.split("/", 2)) for k in a.keys}
    if wanted is not None and not wanted:
        die(2, "give KEY (sheet/id/field) arguments or --all")
    ws, done = wb[SYNC], []
    for r, row in sync_rows(wb):
        key = (norm(row["sheet"]), norm(row["id"]), norm(row["field"]))
        if (wanted is None or key in wanted) and key in state:
            ws.cell(r, 5, state[key])
            ws.cell(r, 6, now())
            done.append("/".join(key))
    backup(book)
    save(wb, book)
    out({"marked_synced": done})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("book"); s.add_argument("--game")
    s = sub.add_parser("dump"); s.add_argument("book"); s.add_argument("--sheet")
    s = sub.add_parser("diff"); s.add_argument("book")
    s = sub.add_parser("ack"); s.add_argument("book"); s.add_argument("--reason")
    s = sub.add_parser("owners"); s.add_argument("book")
    s = sub.add_parser("apply"); s.add_argument("book"); s.add_argument("changes")
    s = sub.add_parser("link"); s.add_argument("book"); s.add_argument("links")
    s = sub.add_parser("sync-status"); s.add_argument("book")
    s = sub.add_parser("mark-synced"); s.add_argument("book"); s.add_argument("keys", nargs="*"); s.add_argument("--all", action="store_true")
    a = p.parse_args()
    {"init": cmd_init, "dump": cmd_dump, "diff": cmd_diff, "ack": cmd_ack, "owners": cmd_owners,
     "apply": cmd_apply, "link": cmd_link, "sync-status": cmd_sync_status,
     "mark-synced": cmd_mark_synced}[a.cmd](a)


if __name__ == "__main__":
    main()
