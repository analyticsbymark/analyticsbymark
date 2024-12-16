from docs_src.bar_chart.tutorial_001 import fig, primary_data, secondary_data, months


def test_001_figure():
    assert "data" in fig
    assert "layout" in fig
    assert list(fig["data"][0]["x"]) == months
    assert list(fig["data"][1]["x"]) == months
    assert list(fig["data"][0]["y"]) == primary_data
    assert list(fig["data"][1]["y"]) == secondary_data
