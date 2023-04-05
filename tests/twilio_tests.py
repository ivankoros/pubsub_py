import pytest
from unittest.mock import MagicMock
from twilio_app import get_user, start_action, get_name_action, get_store_location_action, get_sale_action, default_action
from resources import Users, SubDeal

def test_get_user():
    """Checks if the get_user function correctly initializes a new user

    When no existing user with the provided phone number is found in the database, create a new user.
    This ensures that the new user is created with the correct phone number and state.

    """
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.first.return_value = None
    request_mock = MagicMock()
    request_mock.values.get.return_value = "1234567890"

    user = get_user(session_mock)

    assert user.phone_number == "1234567890"
    assert user.state == 'start'

def test_start_action():
    """Verify if the start state can be transitioned to through the start_action function

    :return: next_state, message (the state to transition the user to and the message received by the Flask app)
    """
    next_state, message = start_action()
    assert next_state == 'get_name'

def test_get_name_action():
    """Verify if the get_name state can be transitioned to through the get_name_action function

    This test checks if the get_name_action function correctly updates the user's name
    based on the provided input and changes the next_state to 'get_store_location'.

    :return: next_state, message (the state to transition the user to and the message received by the Flask app)
    """
    body = "John Doe"
    session_mock = MagicMock()
    user = Users(phone_number="1234567890", name="John Doe", selected_store_address='Sesame Street',
                 state='start')

    next_state, message = get_name_action(body, session_mock, user)

    assert user.name == "John Doe"
    assert next_state == 'get_store_location'

def test_get_store_location_action():
    """Verify if the get_store_location state can be transitioned to through the get_store_location_action function

    This test verifies if the get_store_location_action function correctly updates the user's
    selected_store_address based on the provided input and changes the next_state to 'get_sale'.

    :return: next_state, message (the state to transition the user to and the message received by the Flask app)
    """
    body = "123 Main St"
    session_mock = MagicMock()
    user = Users(phone_number="1234567890", name="John Doe", selected_store_address='Sesame Street',
                 state='get_name')

    next_state, message = get_store_location_action(body, session_mock, user)

    assert user.selected_store_address == "123 Main St"
    assert next_state == 'get_sale'

def test_get_sale_action():
    """Verify if the get_sale state can be transitioned to through the get_sale_action function

    This test checks if the get_sale_action function retrieves the correct sale information
    from the database and generates an appropriate message based on the available sales.
    Tt also ensures that the next_state is set to 'default'.

    :return: next_state, message (the state to transition the user to and the message received by the Flask app)
    """

    body = ""
    session_mock = MagicMock()
    user = Users(phone_number="1234567890", name="John Doe", state='get_store_location',
                 selected_store_address="123 Main St")
    sale = SubDeal(name="Tuna Sub", date="2023-04-05", location="123 Main St")
    session_mock.query.return_value.filter.return_value.all.return_value = [sale]

    next_state, message = get_sale_action(body, session_mock, user)

    assert message == "The tuna sub is on sale today!"
    assert next_state == 'default'

def test_default_action():
    """Verify if the default state can be transitioned to through the default_action function

    This test verifies that the default_action function correctly sets the next_state to 'default'.

    :return: next_state, message (the state to transition the user to and the message received by the Flask app)
    """
    next_state, message = default_action()
    assert next_state == 'default'


if __name__ == "__main__":
    pytest.main()
