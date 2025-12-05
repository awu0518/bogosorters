import security.security as sec


def test_read():
    recs = sec.read()
    assert isinstance(recs, dict)
    for feature in recs:
        assert isinstance(feature, str)
        assert len(feature) > 0


def test_permissions():
    # valid user
    assert sec.has_permission("ejc369@nyu.edu", sec.PEOPLE, sec.CREATE) is True
    # Unknown user 
    assert sec.has_permission('sdljkf@nyu.edu', sec.PEOPLE, sec.CREATE) is False
