import json
import re
from contextlib import suppress
from pathlib import Path


BASE_TEMPLATES = ["templates/base.html", "templates/base_no_nav.html"]

TEMPLATE_PREFIXES = ["base", "_base"]

TAG_NAMES = ["name", "title", "description", "link"]


def is_index(path):
    return path.name == "index.html"


def has_index(path):
    return (path / "index.html").exists()


def is_template(path):
    """
    Return True if the file name starts with a template prefix.

    TODO: It is possible that valid page uris start with one of these prefixes.
    Instead, we could match the extended_path in index.html to files in the
    folder, and exclude files whose filename is in the extended path.
    """
    for prefix in TEMPLATE_PREFIXES:
        if path.name.startswith(prefix):
            return True
    return False


def tags_found(tag_map, keys=TAG_NAMES):
    """Return False if specified keys in a dictionary have None values"""
    for key in keys:
        if tag_map.get(key) is None:
            return False
    return True


def clean_tag(tag):
    """
    TODO:
    Remove nested tags from a given tag

    e.g given the tags

    "Search results{% if query %} for '{{ query }}'{% endif %}"
    Return "Search results"

    "{% if user_info %}Ubuntu Pro Dashboard{% else %}Ubuntu Pro{% endif %}"
    Return "Ubuntu Pro Dashboard"
    """


def append_base_path(base, path_name):
    """
    Add the base (root) to a path URI.

    In some cases, e.g with server/maas/thank-you.html, the file refers
    to a path

    """
    path = Path(path_name)
    # If the path_name has the same prefix as base, we do not
    # append
    if path.parts[0] == base:
        return Path(path_name)
    return Path(base) / path_name


def extends_base(path, base="templates"):
    """Return true if path extends templates/base.html"""
    # TODO: Investigate whether path.read_text performs better than opening
    # a file
    with suppress(FileNotFoundError):
        with path.open("r") as f:
            for line in f.readlines():
                # TODO: also match single quotes \'
                if match := re.search('{% extends "(.*)" %}', line):
                    if match.group(1) in BASE_TEMPLATES:
                        return True
                    else:
                        # HOW DO WE GET IT TO REFER TO BASE PATH?
                        new_path = append_base_path(base, match.group(1))
                        return extends_base(new_path, base=base)
    return False


def get_tags(path):
    """Return title, description, link, children"""
    tags = create_node()

    uri = str(path)
    if uri.endswith("index.html"):
        tags["name"] = str(path).replace("/index.html", "")
    else:
        tags["name"] = str(path).replace(".html", "")

    with path.open("r") as f:
        for line in f.readlines():
            if match := re.search("{% block title %}(.*){% endblock", line):
                tags["title"] = match.group(1)
                continue
            if match := re.search(
                "{% block meta_description %}(.*){% endblock",
                line,
            ):
                tags["description"] = match.group(1)
                continue
            if match := re.search(
                "{% block meta_copydoc %}(.*){% endblock",
                line,
            ):
                tags["link"] = match.group(1)
                continue

            # If all tags are found, return
            if tags_found(tags):
                return tags

        return tags


def is_valid_page(path, extended_path, base="templates"):
    """
    Determine if path is a valid page. Pages are valid if:
    - They contain the same extended path as the index html.
    - Or they extend from the base html.
    """
    if is_template(path):
        return False

    with path.open("r") as f:
        for line in f.readlines():
            if match := re.search('{% extends "(.*)" %}', line):
                if match.group(1) == extended_path:
                    return True
    # If the file does not share the extended path, check if it extends the
    # base html
    return extends_base(path, base=base)


def get_extended_path(path):
    """Get the path extended by the file"""
    with path.open("r") as f:
        for line in f.readlines():
            # TODO: also match single quotes \'
            if match := re.search('{% extends "(.*)" %}', line):
                return match.group(1)


def update_tags(tags, new_tags):
    """
    Update the old tags with new tags if they are not None
    """
    for key in new_tags:
        if new_tags[key] is not None:
            tags[key] = new_tags[key]
    return tags


def create_node():
    """Return a fresh copy of a node from a template"""
    return {
        "name": None,
        "title": None,
        "description": None,
        "link": None,
        "children": [],
    }


def scan_directory(path_name):
    node_path = Path(path_name)
    node = create_node()
    node["name"] = node_path.name
    base = node_path.parts[0]
    extended_path = None

    # Check if an index.html file exists in this directory
    if has_index(node_path):
        index_path = node_path / "index.html"
        # Get the path extended by the index.html file
        extended_path = get_extended_path(index_path)
        # If the file is valid, add it as a child
        if is_valid_page(index_path, extended_path, base=base):
            # Get tags, add as child
            tags = get_tags(index_path)
            node = update_tags(node, tags)

    # Cycle through other files in this directory
    for child in node_path.iterdir():
        # If the child is a file, check if it is a valid page
        if child.is_file() and not is_index(child):
            # If the file is valid, add it as a child
            if is_valid_page(child, extended_path, base=base):
                node["children"].append(get_tags(child))
        # If the child is a directory, scan it
        if child.is_dir():
            child_node = scan_directory(str(child))
            if child_node.get("title") or child_node.get("children"):
                node["children"].append(child_node)

    return node


if __name__ == "__main__":
    tree = scan_directory("templates")
    print(json.dumps(tree, indent=4))
