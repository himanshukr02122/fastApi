def test_is_equal_or_not():
    assert 3 == 3

def test_list():
    num_list = [1,2,3,4,5]
    any_list = [True, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert any(any_list)