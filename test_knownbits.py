from hypothesis import given, strategies, settings
import pytest

from knownbits import KnownBits


_build_knownbits_and_contained_value = \
    lambda concrete, unknown: (KnownBits(concrete & ~unknown, unknown), concrete)

_random_knownbits_and_contained_value = strategies.builds(
    _build_knownbits_and_contained_value,
    strategies.integers(),
    strategies.integers(),
)

_constant_knownbits = strategies.builds(
    lambda value: (KnownBits.from_constant(value), value),
    strategies.integers(),
)

_knownbits_and_contained_value = _random_knownbits_and_contained_value | _constant_knownbits


def test_knownbits_to_str():
    assert str(KnownBits.from_constant(0)) == '0'
    assert str(KnownBits.from_constant(5)) == '101'
    assert str(KnownBits(5, 0b010)) == '1?1'
    assert str(KnownBits(~0b1111, 0b10)) == '...100?0'
    assert str(KnownBits(1, ~0b1)) == '...?1'


@given(_knownbits_and_contained_value)
def test_str_roundtrip(t1):
    k1, _ = t1
    k2 = KnownBits.from_str(str(k1))
    assert k1.ones == k2.ones
    assert k1.unknowns == k2.unknowns


@given(_knownbits_and_contained_value)
def test_contains(t):
    k, n = t
    assert k.contains(n)


def test_invert_simple():
    k1 = KnownBits.from_str("01?01?01?")
    k2 = ~k1
    assert str(k2) == "...10?10?10?"

    k1 = KnownBits.from_str("...?")
    k2 = ~k1
    assert str(k2) == "...?"


@given(_knownbits_and_contained_value)
def test_hypothesis_invert(t):
    k1, n1 = t
    k2, n2 = ~k1, ~n1
    assert k2.contains(n2)


def test_and_simple():
    k1       = KnownBits.from_str("01?01?01?")
    k2       = KnownBits.from_str("000111???")
    expected = KnownBits.from_str("00001?0??")
    assert k1 & k2 == expected


@given(_knownbits_and_contained_value, _knownbits_and_contained_value)
def test_hypothesis_and(t1, t2):
    (k1, n1), (k2, n2) = t1, t2
    k3, n3 = k1 & k2, n1 & n2
    assert k3.contains(n3)


def test_or_simple():
    k1       = KnownBits.from_str("01?01?01?")
    k2       = KnownBits.from_str("000111???")
    expected = KnownBits.from_str("01?11??1?")
    assert k1 | k2 == expected


@given(_knownbits_and_contained_value, _knownbits_and_contained_value)
def test_hypothesis_or(t1, t2):
    (k1, n1), (k2, n2) = t1, t2
    k3, n3 = k1 | k2, n1 | n2
    assert k3.contains(n3)


def test_add_simple():
    k1       = KnownBits.from_str("0?10?10?10")
    k2       = KnownBits.from_str("0???111000")
    expected = KnownBits.from_str("?????01?10")
    assert k1 + k2 == expected


@given(_knownbits_and_contained_value, _knownbits_and_contained_value)
def test_hypothesis_add(t1, t2):
    (k1, n1), (k2, n2) = t1, t2
    k3, n3 = k1 + k2, n1 + n2
    assert k3.contains(n3)


def test_sub_simple():
    k1       = KnownBits.from_str("0?10?10?10")
    k2       = KnownBits.from_str("0???111000")
    expected = KnownBits.from_str("?????11?10")
    assert k1 - k2 == expected

    k1       = KnownBits.from_str(    "...1?10?10?10")
    k2       = KnownBits.from_str("...10000???111000")
    expected = KnownBits.from_str(    "111?????11?10")
    assert k1 - k2 == expected


@given(_knownbits_and_contained_value, _knownbits_and_contained_value)
def test_hypothesis_sub(t1, t2):
    (k1, n1), (k2, n2) = t1, t2
    k3, n3 = k1 - k2, n1 - n2
    assert k3.contains(n3)
