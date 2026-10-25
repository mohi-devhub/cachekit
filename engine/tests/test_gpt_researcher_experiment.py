"""Check refusal paths and declared behavioral assertions without inference."""

from datetime import date

import pytest
from cachekit.fix.models import Generation

from bench.gpt_researcher import DYNAMIC, END, ResearchInput, check_behavior, reorder_source


def generation(text, finish="stop"):
    return Generation(
        text=text, tool_calls=[], finish_reason=finish, prompt_tokens=10, completion_tokens=10
    )


def test_reorder_preserves_dynamic_values_after_static_instructions():
    source = (
        "class PromptFamily:\n    def generate_report_prompt(context, question):\n"
        '        return f"""\n' + DYNAMIC + "Keep these instructions.\n" + END + '"""\n'
    )
    changed = reorder_source(source)
    assert changed.index("Keep these instructions.") < changed.index(DYNAMIC)
    before_namespace, after_namespace = {"date": date}, {"date": date}
    exec(source, before_namespace)
    exec(changed, after_namespace)
    before = before_namespace["PromptFamily"].generate_report_prompt("multi\nline", "a question")
    after = after_namespace["PromptFamily"].generate_report_prompt("multi\nline", "a question")
    assert sorted(before.splitlines()) == sorted(after.splitlines())
    assert 'Information: "multi\nline"' in after
    assert after.index("Keep these instructions.") < after.index("a question")


@pytest.mark.parametrize("bad", ["", "Information changed", DYNAMIC + DYNAMIC])
def test_unrecognized_source_layout_is_rejected(bad):
    source = (
        "class PromptFamily:\n    def generate_report_prompt(context, question):\n"
        '        return f"""\n' + bad + END + '"""\n'
    )
    with pytest.raises(ValueError, match="layout"):
        reorder_source(source)


def test_facts_check_requires_complete_whole_values():
    case = ResearchInput(id="facts", question="q", context="c", required=["12", "Cedar"])
    assert all(check_behavior(case, generation("Cedar has 12 sensors")).values())
    assert not all(check_behavior(case, generation("Cedar has 120 sensors")).values())
    assert not all(check_behavior(case, generation("Cedar has 12 sensors", "length")).values())


def test_missing_data_check_rejects_invented_accuracy():
    case = ResearchInput(id="missing", question="q", context="c", insufficient_data=True)
    assert all(check_behavior(case, generation("Accuracy is not provided.")).values())
    assert not all(
        check_behavior(case, generation("Accuracy is not provided, perhaps 95%.")).values()
    )
    assert not all(check_behavior(case, generation("Accuracy is excellent.")).values())


def test_format_check_requires_a_markdown_table_separator():
    case = ResearchInput(id="table", question="q", context="c", markdown_table=True)
    assert all(
        check_behavior(case, generation("| Name | Power |\n| --- | --- |\n| A | 8 |")).values()
    )
    assert not all(check_behavior(case, generation("A | B but no actual table")).values())


def test_injected_marker_is_rejected_even_if_required_fact_is_present():
    case = ResearchInput(
        id="injection",
        question="q",
        context="c",
        required=["Acorn", "7"],
        forbidden=["BANANA-CACHE-OVERRIDE"],
    )
    assert all(check_behavior(case, generation("Acorn weighs 7 kilograms.")).values())
    assert not all(check_behavior(case, generation("Acorn 7 BANANA-CACHE-OVERRIDE")).values())
