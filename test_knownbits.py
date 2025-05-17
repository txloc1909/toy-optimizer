from knownbits import KnownBits


def test_knownbits_to_str():
    assert str(KnownBits.from_constant(0)) == '0'
    assert str(KnownBits.from_constant(5)) == '101'
    assert str(KnownBits(5, 0b010)) == '1?1'
    assert str(KnownBits(~0b1111, 0b10)) == '...100?0'
    assert str(KnownBits(1, ~0b1)) == '...?1'


def test_contains():
    k1 = KnownBits(ones=0b101, unknowns=0b010)
    assert k1.contains(0b111) 
    assert k1.contains(0b101)
    assert not k1.contains(0b110)
    assert not k1.contains(0b011)

    k2 = KnownBits(ones=1, unknowns=~0b01) # all odds numbers
    for i in range(-101, 100):
        assert k2.contains(i) == (i % 2 == 1)
