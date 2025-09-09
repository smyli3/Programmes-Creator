#!/usr/bin/env python
"""
Data Import Tools

Usage examples (from project root):
  # 1) Diagnostics
  # Lists all programs with student counts and count of bad sentinel emails
  # (Run inside your venv; FLASK_APP is not required for this script)
  #   python scripts/data_import_tools.py diagnostics

  # 2) Clear a program's data (students, groups, memberships) for clean re-import
  #   python scripts/data_import_tools.py clear --program-id <PROGRAM_ID>

  # 3) Fix existing students (replace 'hoh'/'guest' emails with blank) and re-upload with Update
  #   python scripts/data_import_tools.py fix-emails --program-id <PROGRAM_ID>

"""
from __future__ import annotations
import sys
import argparse

from app import create_app
from app.extensions import db
from app.models import Program, Student, Group, Membership


def diagnostics() -> int:
    app = create_app()
    with app.app_context():
        print("=== PROGRAM ANALYSIS ===")
        programs = Program.query.all()
        if not programs:
            print("No programs found.")
        for p in programs:
            student_count = Student.query.filter_by(program_id=p.id).count()
            print(f"Program: {p.name} (ID: {p.id}) | Students: {student_count}")

        print("\n=== DATA QUALITY ISSUES ===")
        bad_emails = Student.query.filter(Student.contact_email.in_(["hoh", "guest", "HOH", "Guest"]))
        print(f"Students with bad sentinel emails: {bad_emails.count()}")

        with_customer_id = Student.query.filter(Student.customer_id.isnot(None), Student.customer_id != "").count()
        print(f"Students with customer_id: {with_customer_id}")

        with_name_dob = Student.query.filter(Student.name != "", Student.birth_date.isnot(None)).count()
        print(f"Students with name+birthdate: {with_name_dob}")

        print("\n=== WEEKLY ASSIGNMENTS (active memberships by week) ===")
        for p in programs:
            any_week = False
            max_weeks = p.max_weeks or 6
            for week in range(1, max_weeks + 1):
                active_members = (
                    db.session.query(Membership)
                    .join(Group, Group.id == Membership.group_id)
                    .filter(
                        Group.program_id == p.id,
                        Membership.week_number == week,
                        Membership.is_active == True,
                    )
                    .count()
                )
                if active_members > 0:
                    print(f"{p.name} Week {week}: {active_members} active assignments")
                    any_week = True
            if not any_week:
                print(f"{p.name}: no active weekly assignments found")
    return 0


def clear_program(program_id: str) -> int:
    if not program_id:
        print("--program-id is required for clear action", file=sys.stderr)
        return 2

    app = create_app()
    with app.app_context():
        prog = Program.query.get(program_id)
        if not prog:
            print(f"Program not found: {program_id}", file=sys.stderr)
            return 3

        print(f"Clearing data for program: {prog.name} ({prog.id})")

        group_ids = [g.id for g in Group.query.filter_by(program_id=program_id).all()]
        deleted_memberships = 0
        deleted_groups = 0
        if group_ids:
            deleted_memberships = (
                Membership.query.filter(Membership.group_id.in_(group_ids)).delete(synchronize_session=False)
            )
            deleted_groups = Group.query.filter_by(program_id=program_id).delete()
        deleted_students = Student.query.filter_by(program_id=program_id).delete(synchronize_session=False)

        db.session.commit()
        print(f"Deleted {deleted_memberships} memberships, {deleted_groups} groups, {deleted_students} students")
        print("Program data cleared successfully. Re-upload with 'Allow duplicates' or 'Update existing'.")
    return 0


def fix_emails(program_id: str) -> int:
    if not program_id:
        print("--program-id is required for fix-emails action", file=sys.stderr)
        return 2

    app = create_app()
    with app.app_context():
        prog = Program.query.get(program_id)
        if not prog:
            print(f"Program not found: {program_id}", file=sys.stderr)
            return 3

        print(f"Cleaning sentinel emails for program: {prog.name} ({prog.id})")
        students = Student.query.filter_by(program_id=program_id).all()
        updated = 0
        for s in students:
            if s.contact_email and s.contact_email.lower() in {"hoh", "guest"}:
                s.contact_email = ""
                updated += 1
        db.session.commit()
        print(f"Cleaned {updated} bad email values. Re-upload with 'Update existing'.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Data import diagnostics and fixes.")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("diagnostics", help="Print programs, student counts, and data quality issues")

    p_clear = sub.add_parser("clear", help="Clear students, groups, memberships for a program")
    p_clear.add_argument("--program-id", required=True, help="Target Program UUID")

    p_fix = sub.add_parser("fix-emails", help="Replace 'hoh'/'guest' emails with blank for a program")
    p_fix.add_argument("--program-id", required=True, help="Target Program UUID")

    args = parser.parse_args(argv)

    if args.action == "diagnostics":
        return diagnostics()
    elif args.action == "clear":
        return clear_program(args.program_id)
    elif args.action == "fix-emails":
        return fix_emails(args.program_id)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
