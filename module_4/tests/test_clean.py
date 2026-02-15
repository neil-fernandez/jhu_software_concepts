import pytest

import clean as clean_module


@pytest.mark.integration
def test_clean_data_parses_rows_and_details():
    # test clean_data parses overview rows, detail rows, and fallback fields
    html = """
    <table>
        <tr>
            <td>Detail without last row</td>
        </tr>
        <tr>
            <td>Example University <a href="/result/abc">Overview</a></td>
            <td>Computer Science</td>
            <td>January 10, 2025</td>
        </tr>
        <tr>
            <td colspan="3">
                <div>Accepted on 12 Feb 2025</div>
                <div>PhD</div>
                <p>Great program</p>
                Fall 2026 International GRE 330 GRE V 165 GRE AW 4.5 GPA 3.90
            </td>
        </tr>
        <tr>
            <td colspan="3">
                <div>Rejected on 1 Mar 2025</div>
                <p>Second comment</p>
                Spring 2027 Domestic
            </td>
        </tr>
        <tr>
            <td>Another University <a href="https://www.thegradcafe.com/result/xyz">Overview</a></td>
            <td>Data Science</td>
        </tr>
        <tr>
            <td colspan="2">
                Wait listed on 3 Apr 2025 US Citizen GRE 320 GRE V 160 GRE AW 4.0 GPA 3.80 MS
                <p>Second row comment</p>
            </td>
        </tr>
    </table>
    """

    results = clean_module.clean_data(html)

    assert len(results) == 2

    first = results[0]
    assert first["program"] == "Computer Science, Example University Overview"
    assert first["url"] == "https://www.thegradcafe.com/result/abc"
    assert first["date_added"] == "January 10, 2025"
    assert first["semester_year_start"] == "Fall 2026"
    assert first["applicant_status"] == "Accepted"
    assert first["status_date"] == "12 Feb 2025"
    assert first["citizenship"] == "International"
    assert first["gre"] == "330"
    assert first["gre_v"] == "165"
    assert first["gre_aw"] == "4.5"
    assert first["gpa"] == "3.90"
    assert first["masters_or_phd"] == "PhD"
    assert first["comments"] == "Great program"

    second = results[1]
    assert second["program"] == "Data Science, Another University Overview"
    assert second["url"] == "https://www.thegradcafe.com/result/xyz"
    assert second["date_added"] == ""
    assert second["semester_year_start"] == ""
    assert second["applicant_status"] == "Wait listed"
    assert second["status_date"] == "3 Apr 2025"
    assert second["citizenship"] == "US Citizen"
    assert second["gre"] == "320"
    assert second["gre_v"] == "160"
    assert second["gre_aw"] == "4.0"
    assert second["gpa"] == "3.80"
    assert second["masters_or_phd"] == "Masters"
    assert second["comments"] == "Second row comment"


@pytest.mark.integration
def test_clean_data_returns_empty_list_when_no_rows():
    # test clean_data returns empty list when no table rows exist
    html = "<table></table>"
    assert clean_module.clean_data(html) == []
