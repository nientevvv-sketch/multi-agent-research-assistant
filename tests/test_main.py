
import main as main_module


def test_save_report_creates_markdown_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        main_module,
        "REPORTS_DIR",
        tmp_path
    )

    result = {
        "plan": {
            "goal": "Study AI in finance",
            "tasks": [
                "Research current applications",
                "Analyse financial risks"
            ]
        },
        "research_material": "AI is used in financial analysis.",
        "sources": [
            {
                "title": "AI in Finance",
                "url": "https://example.com/ai-finance",
                "source_type": "Wikipedia article",
                "authors": ["John Smith"],
                "published": "2025",
                "content": "Research about AI in finance."
            }
        ],
        "analysis": "AI can improve financial decision-making.",
        "fact_check": "The findings require further verification.",
        "final_report": "Final report about AI in finance."
    }

    report_path = main_module.save_report(
        result,
        "How is AI used in finance?"
    )

    assert report_path.exists()
    assert report_path.suffix == ".md"

    content = report_path.read_text(encoding="utf-8")

    assert "# Research Report" in content
    assert "How is AI used in finance?" in content
    assert "Study AI in finance" in content
    assert "Research current applications" in content
    assert "AI can improve financial decision-making." in content
    assert "Final report about AI in finance." in content
    assert "AI in Finance" in content
    assert "https://example.com/ai-finance" in content


def test_save_report_handles_empty_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(
        main_module,
        "REPORTS_DIR",
        tmp_path
    )

    result = {
        "plan": {},
        "research_material": "",
        "sources": [],
        "analysis": "",
        "fact_check": "",
        "final_report": "Test report."
    }

    report_path = main_module.save_report(
        result,
        "Test research question"
    )

    content = report_path.read_text(encoding="utf-8")

    assert report_path.exists()
    assert "No sources were collected." in content
    assert "Test report." in content
