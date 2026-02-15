import pytest
from flask import Flask
from bs4 import BeautifulSoup

import app as flask_app_module  # load app for testing Flask app object


@pytest.fixture()
def app():
    flask_app = flask_app_module.create_app()  # get the Flask app instance
    flask_app.config["TESTING"] = True  # enable test mode
    flask_app.config["LIVESERVER_PORT"] = 8080
    flask_app.config["LIVESERVER_TIMEOUT"] = 10

    yield flask_app


# provide test client that simulates HTTP requests to app without a live server
@pytest.fixture()
def client(app):
    return app.test_client()


# test that app is valid Flask app created in test mode (i.e. testable)
@pytest.mark.web
def test_app_is_flask_instance_and_testable(app):
    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True


# test that all routes have been created and each route allows the correct HTTP request type
@pytest.mark.web
def test_app_routes_are_created(app):
    routes = {rule.rule: rule.methods for rule in app.url_map.iter_rules()}

    assert "/" in routes
    assert "GET" in routes["/"]

    assert "/analysis" in routes
    assert "GET" in routes["/analysis"]

    assert "/pull-data" in routes
    assert "POST" in routes["/pull-data"]


# test GET /analysis page load returns Status 200
@pytest.mark.web
def test_get_analysis_returns_200(client):
    response = client.get("/analysis", query_string={"skip_queries": "1"})
    assert response.status_code == 200


# test GET "/analysis" page contains both "Pull Data" and "Update Analysis" button elements and labels
@pytest.mark.web
def test_get_analysis_contains_page_buttons(client):
    response = client.get("/analysis", query_string={"skip_queries": "1"})
    soup = BeautifulSoup(response.get_data(as_text=True), "html.parser")

    pull_btn = soup.find("button", id="pull-data-button")
    update_btn = soup.find("button", id="update-analysis-button")

    assert pull_btn is not None
    assert update_btn is not None

    assert pull_btn.get("data-testid") == "pull-data-btn"
    assert update_btn.get("data-testid") == "update-analysis-btn"
    assert pull_btn.get_text(strip=True) == "Pull Data"
    assert update_btn.get_text(strip=True) == "Update Analysis"


# test GET "/analysis" page text includes "Analysis" and at least one "Answer" label
@pytest.mark.web
def test_get_analysis_contains_page_content(client):
    response = client.get("/analysis", query_string={"skip_queries": "1"})

    page = response.get_data(as_text=True)  # get text from HTML bytes
    assert "Analysis" in page   # assert page includes "Analysis" text
    assert "Answer" in page # assert page includes "Answer" text
