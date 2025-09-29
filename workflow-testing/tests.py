import pytest
from main import graph


@pytest.mark.parametrize(
    "email, expected_category, expected_score",
    [
        ("this is urgent!", "urgent", 10),
        ("i wanna talk to you", "normal", 5),
        ("i have an offer for you", "spam", 1),
    ],
)
def test_full_graph(email, expected_category, expected_score):

    result = graph.invoke({"email": email}, config={"configurable": {"thread_id": "1"}})

    assert result["category"] == expected_category
    assert result["priority_score"] == expected_score


def test_individual_nodes():

    # categorize_email
    result = graph.nodes["categorize_email"].invoke({"email": "check out this offer"})

    assert result["category"] == "spam"

    # assing_priority

    result = graph.nodes["assing_priority"].invoke({"category": "spam"})

    assert result["priority_score"] == 1

    # draft_response

    result = graph.nodes["draft_response"].invoke({"category": "spam"})

    assert "Go away" in result["response"]


def test_partial_execution():

    graph.update_state(
        config={
            "configurable": {
                "thread_id": "1",
            },
        },
        values={
            "email": "please check out this offer",
            "category": "spam",
        },
        as_node="categorize_email",
    )

    result = graph.invoke(
        None,
        config={
            "configurable": {
                "thread_id": "1",
            },
        },
        interrupt_after="draft_response",
    )

    assert result["priority_score"] == 1
