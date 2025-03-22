import pytest
from boxing.models.boxers_model import get_weight_class

def test_get_weight_class_heavyweight():
    assert get_weight_class(210) == "HEAVYWEIGHT"

def test_get_weight_class_middleweight():
    assert get_weight_class(170) == "MIDDLEWEIGHT"

def test_get_weight_class_invalid_weight():
    with pytest.raises(ValueError):
        get_weight_class(120)
