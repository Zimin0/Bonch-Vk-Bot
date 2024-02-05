from typing import Dict

from diagrams import Node, getdiagram, getcluster, Diagram


class NewDiagram(Diagram):
    _default_graph_attrs = {
        "pad": "1.0",
        "splines": "ortho",
        "nodesep": "0.60",
        "ranksep": "0.60",
        "fontname": "Arial",
        "fontsize": "16",
        "fontcolor": "#303136",
        "bgcolor": "#c3d0e0",
    }
    _default_node_attrs = {
        "shape": "box",
        "style": "rounded",
        "fixedsize": "true",
        "width": "2",
        "height": "0.4",
        "labelloc": "b",
        "imagescale": "true",
        "fontname": "Arial",
        "fontsize": "14",
        "fontcolor": "#303136",
    }
    _default_edge_attrs = {
        "color": "#303136",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NewCustom(Node):
    _provider = "custom"
    _type = "custom"
    _icon_dir = None

    fontcolor = "#ffffff"

    _height = 0.45

    def _load_icon(self):
        return self._icon

    def __init__(self, icon_path, label: str = "", **attrs: Dict):
        self._icon = icon_path
        self._id = self._rand_id()
        self.label = label

        self._attrs = {
            "shape": "box",
            "height": str(self._height),
            "image": self._load_icon(),
        } if self._icon else {}

        self._attrs.update(attrs)

        self._diagram = getdiagram()
        if self._diagram is None:
            raise EnvironmentError("Global diagrams context not set up")
        self._cluster = getcluster()

        if self._cluster:
            self._cluster.node(self._id, self.label, **self._attrs)
        else:
            self._diagram.node(self._id, self.label, **self._attrs)
