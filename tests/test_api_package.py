"""The Python engine API (incognita.engine), no data needed."""
from incognita.engine import channel_label


def test_channel_label():
    assert channel_label("xs000000") == "(n,g)"
    assert channel_label("xs200000") == "(n,2n)"
    assert channel_label("xs010000") == "(n,p)"
    assert channel_label("xs110000") == "(n,np)"
    assert channel_label("xs000001") == "(n,a)"
    assert channel_label("total") == "total"

