from canonicalwebteam.templateparser.parse_tree import (
    has_index,
    is_index,
    extends_base,
)


def test_has_index(tmp_path):
    # Create test directory
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    # Create index.html file
    index = test_dir / "index.html"
    index.touch()

    assert has_index(test_dir) is True

    # Create empty directory
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    assert has_index(empty_dir) is False


def test_is_index(tmp_path):
    # Create index.html file
    index = tmp_path / "index.html"
    index.touch()

    assert is_index(index) is True

    # Create non index.html file
    non_index = tmp_path / "non_index.html"
    non_index.touch()

    assert is_index(non_index) is False


def test_extends_base(tmp_path):
    # Create extending index.html file
    index = tmp_path / "index.html"
    index.touch()
    index.write_text('{% extends "templates/base.html" %}')

    assert extends_base(index) is True

    # Create non extending index.html file
    non_base = tmp_path / "non_base.html"
    non_base.touch()
    non_base.write_text('{% extends templates/non_base.html" %}')

    assert extends_base(non_base) is False

    # Create empty index.html file
    empty_index = tmp_path / "empty_index.html"
    empty_index.touch()

    assert extends_base(empty_index) is False

    # Check index.html with deeply nested extends
    nested_index = tmp_path / "nested_index.html"
    nested_index.touch()
    nested_index.write_text(
        '{% extends "'
        + str(tmp_path.absolute())
        + '/nested_index_two.html" %}'
    )

    nested_index_two = tmp_path / "nested_index_two.html"
    nested_index_two.touch()
    nested_index_two.write_text(
        '{% extends "'
        + str(tmp_path.absolute())
        + '/nested_index_three.html" %}'
    )

    nested_index_three = tmp_path / "nested_index_three.html"
    nested_index_three.touch()
    nested_index_three.write_text(
        '{% extends "' + str(tmp_path.absolute()) + '/base.html" %}'
    )

    assert (
        extends_base(nested_index, base_dir=str(tmp_path.absolute())) is True
    )
