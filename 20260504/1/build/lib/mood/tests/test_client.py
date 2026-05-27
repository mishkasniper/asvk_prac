import pytest
from mood.client.client import MUDClient


@pytest.fixture
def mock_client():
    return MUDClient("tester", testing=True)


def test_move_up(mock_client):
    mock_client.do_up("")
    mock_client.send_command.assert_called_once_with("move -1 0")


def test_move_down(mock_client):
    mock_client.do_down("")
    mock_client.send_command.assert_called_once_with("move 1 0")


def test_move_left(mock_client):
    mock_client.do_left("")
    mock_client.send_command.assert_called_once_with("move 0 -1")


def test_move_right(mock_client):
    mock_client.do_right("")
    mock_client.send_command.assert_called_once_with("move 0 1")


def test_attack_default_sword(mock_client):
    """attack dragon -> attack dragon 10"""
    mock_client.do_attack("dragon")
    mock_client.send_command.assert_called_once_with("attack dragon 10")


def test_attack_with_spear(mock_client):
    """attack dragon with spear -> attack dragon 15"""
    mock_client.do_attack("dragon with spear")
    mock_client.send_command.assert_called_once_with("attack dragon 15")


def test_attack_with_axe(mock_client):
    """attack dragon with axe -> attack dragon 20"""
    mock_client.do_attack("dragon with axe")
    mock_client.send_command.assert_called_once_with("attack dragon 20")


def test_attack_no_args(mock_client):
    """attack без аргументов -> ошибка, send_command не вызывается"""
    mock_client.do_attack("")
    mock_client.send_command.assert_not_called()


def test_attack_unknown_weapon(mock_client):
    """attack dragon with hammer -> ошибка"""
    mock_client.do_attack("dragon with hammer")
    mock_client.send_command.assert_not_called()


def test_attack_invalid_syntax(mock_client):
    """attack dragon sword (пропущено 'with') -> ошибка"""
    mock_client.do_attack("dragon sword")
    mock_client.send_command.assert_not_called()


def test_attack_too_many_args(mock_client):
    """attack dragon with sword extra -> ошибка"""
    mock_client.do_attack("dragon with sword extra")
    mock_client.send_command.assert_not_called()
