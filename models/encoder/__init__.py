"""Stage A chart encoders (blueprint §5.2)."""

from models.encoder.chart_cnn import ChartCNN, HeadSpec
from models.encoder.gnn import ChartGNN

ENCODERS = {"cnn": ChartCNN, "gnn": ChartGNN}


def make_encoder(arch: dict, heads: list[HeadSpec]):
    """Build an encoder from a saved/declared ``arch`` dict (``encoder`` key selects the class)."""
    arch = dict(arch)
    cls = ENCODERS[arch.pop("encoder", "cnn")]
    return cls(heads=heads, **arch)


__all__ = ["ENCODERS", "ChartCNN", "ChartGNN", "HeadSpec", "make_encoder"]
