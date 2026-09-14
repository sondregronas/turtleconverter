from turtleconverter import ensure_nl2br_forms


def test_forms_do_not_add_blank_lines_to_yaml_literal_scalars():
    content = """\
---
tags: |
  - ${{ github.event || github.ref && github.ref_name }}
---
Body
"""

    assert ensure_nl2br_forms(content) == content


def test_forms_do_not_add_blank_lines_inside_fenced_yaml():
    content = """\
```yaml
tags: |
  - ${{ github.event || github.ref && github.ref_name }}
```
"""

    assert ensure_nl2br_forms(content) == content


def test_forms_preserve_table_spacing():
    content = """\
| Name | Value |
| --- | --- |
| one | 1 |
After
"""

    assert ensure_nl2br_forms(content) == """\
| Name | Value |
| --- | --- |
| one | 1 |

After
"""


def test_forms_preserve_callout_table_spacing():
    content = """\
> Intro
> | Name | Value |
> | --- | --- |
> | one | 1 |
> Next
"""

    assert ensure_nl2br_forms(content) == """\
> Intro
> 
> | Name | Value |
> | --- | --- |
> | one | 1 |
> 
> Next
"""
