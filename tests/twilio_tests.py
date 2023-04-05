import pytest
from unittest.mock import MagicMock
from twilio_app import get_user, start_action, get_name_action, get_store_location_action, get_sale_action, default_action
from resources import Users, SubDeal

def test_get_user():
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.first.return_value = None
    request_mock = MagicMock()
    request_mock.values.get.return_value = "1234567890"

    user = get_user(session_mock)

    assert user.phone_number == "1234567890"
    assert user.state == 'start'

def test_start_action():
    next_state, message = start_action()
    assert next_state == 'get_name'

def test_get_name_action():
    body = "John Doe"
    session_mock = MagicMock()
    user = Users(phone_number="1234567890", state='start')

    next_state, message = get_name_action(body, session_mock, user)

    assert user.name == "John Doe"
    assert next_state == 'get_store_location'

def test_get_store_location_action():
    body = "123 Main St"
    session_mock = MagicMock()
    user = Users(phone_number="1234567890", name="John Doe", state='get_name')

    next_state, message = get_store_location_action(body, session_mock, user)

    assert user.selected_store_address == "123 Main St"
    assert next_state == 'get_sale'

def test_get_sale_action():
    body = ""
    session_mock = MagicMock()
    user = Users(phone_number="1234567890", name="John Doe", state='get_store_location')
    sale = SubDeal(name="Tuna Sub", date="2023-04-05")
    session_mock.query.return_value.filter.return_value.all.return_value = [sale]

    next_state, message = get_sale_action(body, session_mock, user)

    assert message == "The tuna sub is on sale today!"
    assert next_state == 'default'

def test_default_action():
    next_state, message = default_action()
    assert next_state == 'default'


if __name__ == "__main__":
    pytest.main()
