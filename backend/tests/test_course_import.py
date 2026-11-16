import json
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.models import Course as CourseRow, Prerequisite
from app.schemas.course import Course as CourseData, PrerequisiteNode as Node
from app.services.course_import import (
    import_courses,
    make_course_code,
    normalize_dept,
    normalize_number,
    normalize_title,
    parse_credits,
    prerequisite_groups,
)

FIXTURES = Path(__file__).parent / "fixtures"


def course(code, title="Some Course", tree=None, units="3", **kwargs):
    dept, number = code.split()
    return CourseData(dept=dept, number=number, title=title, units=units,
                      prerequisite_tree=tree, **kwargs)


def count(db, model):
    return db.scalar(select(func.count()).select_from(model))


def leaf(code):
    return Node(type="course", id=code)


def get_course(db, code):
    return db.scalar(select(CourseRow).where(CourseRow.course_code == code))


# ---------- Normalizers ----------

@pytest.mark.parametrize("raw, expected", [(" cmpt ", "CMPT"), ("Macm", "MACM")])
def test_normalize_dept(raw, expected):
    assert normalize_dept(raw) == expected


@pytest.mark.parametrize("raw, expected", [("105w ", "105W"), ("225", "225")])
def test_normalize_number(raw, expected):
    assert normalize_number(raw) == expected


def test_normalize_title_collapses_whitespace():
    assert normalize_title("  Data   Structures\n") == "Data Structures"


def test_make_course_code_normalizes_and_adds_space():
    assert make_course_code(" cmpt", "225") == "CMPT 225"


@pytest.mark.parametrize("units, expected", [(None, 0), ("", 0), ("abc", 0), ("3", 3)])
def test_parse_credits(units, expected):
    assert parse_credits(units) == expected


# ---------- Prerequisite tree -> groups ----------

def test_no_tree_has_no_groups():
    assert prerequisite_groups(None) == []


def test_single_course_tree_is_one_group():
    assert prerequisite_groups(leaf("CMPT 125")) == [["CMPT 125"]]


def test_and_tree_is_one_group_per_course():
    tree = Node(type="and", children=[leaf("CMPT 125"), leaf("MACM 101")])
    assert prerequisite_groups(tree) == [["CMPT 125"], ["MACM 101"]]


def test_or_tree_is_one_group():
    tree = Node(type="or", children=[leaf("CMPT 125"), leaf("CMPT 135")])
    assert prerequisite_groups(tree) == [["CMPT 125", "CMPT 135"]]


def test_or_inside_and_becomes_its_own_group():
    tree = Node(type="and", children=[
        leaf("MACM 101"),
        Node(type="or", children=[leaf("CMPT 125"), leaf("CMPT 135")]),
    ])
    assert prerequisite_groups(tree) == [["MACM 101"], ["CMPT 125", "CMPT 135"]]


def test_or_with_non_course_child_has_no_groups():
    tree = Node(type="or", children=[
        leaf("CMPT 125"),
        Node(type="and", children=[leaf("ENSC 251"), leaf("ENSC 252")]),
    ])
    assert prerequisite_groups(tree) == []


# ---------- Importing into the database ----------

def test_first_import_reports_created(db):
    stats = import_courses(db, [course("CMPT 125"), course("CMPT 225")])

    assert stats.created == 2
    assert stats.updated == 0


def test_import_twice_creates_no_duplicates(db):
    tree = Node(type="and", children=[leaf("CMPT 125")])
    batch = [course("CMPT 125"), course("CMPT 225", tree=tree)]

    import_courses(db, batch)
    import_courses(db, batch)

    assert count(db, CourseRow) == 2
    assert count(db, Prerequisite) == 1


def test_reimport_updates_existing_course(db):
    import_courses(db, [course("CMPT 125", title="Old")])
    stats = import_courses(db, [course("CMPT 125", title="New")])

    assert count(db, CourseRow) == 1
    assert get_course(db, "CMPT 125").title == "New"
    assert stats.updated == 1


def test_duplicate_course_in_one_batch_is_stored_once(db):
    tree = Node(type="and", children=[leaf("CMPT 125")])
    batch = [course("CMPT 125"), course("CMPT 225", tree=tree), course("CMPT 225", tree=tree)]

    import_courses(db, batch)

    assert count(db, CourseRow) == 2
    assert count(db, Prerequisite) == 1


def test_prerequisite_links_to_course_from_earlier_import(db):
    import_courses(db, [course("MACM 101")])
    stats = import_courses(db, [course("CMPT 225", tree=Node(type="and", children=[leaf("MACM 101")]))])

    assert stats.prerequisites == 1
    assert count(db, Prerequisite) == 1


def test_unknown_prerequisite_is_skipped(db):
    import_courses(db, [course("CMPT 225", tree=Node(type="and", children=[leaf("MACM 101")]))])

    assert count(db, CourseRow) == 1
    assert count(db, Prerequisite) == 0


def test_prerequisite_removed_upstream_is_deleted(db):
    tree = Node(type="and", children=[leaf("CMPT 125")])
    import_courses(db, [course("CMPT 125"), course("CMPT 225", tree=tree)])

    import_courses(db, [course("CMPT 225", tree=None)])

    assert count(db, Prerequisite) == 0


def test_group_numbers_start_at_one(db):
    tree = Node(type="and", children=[leaf("CMPT 125"), leaf("MACM 101")])
    import_courses(db, [course("CMPT 125"), course("MACM 101"), course("CMPT 225", tree=tree)])

    assert set(db.scalars(select(Prerequisite.group_number)).all()) == {1, 2}


def test_empty_text_fields_are_stored_as_null(db):
    import_courses(db, [course("CMPT 125", description="", prerequisites="", corequisites="")])

    row = get_course(db, "CMPT 125")
    assert row.description is None
    assert row.prerequisites_text is None
    assert row.corequisites_text is None


def test_imports_fixture_outline(db):
    outlines = json.loads((FIXTURES / "course_outlines.json").read_text(encoding="utf-8"))

    import_courses(db, [CourseData(**item) for item in outlines])

    row = get_course(db, "CMPT 225")
    assert row.credits == 3
    assert row.title == "Data Structures and Programming"
    assert row.prerequisites_text == "CMPT 125 and MACM 101."
