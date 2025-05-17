from hypothesis import given, strategies, settings

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
