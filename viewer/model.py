"""Mock OpenSeesPy module for intercepting ops.node(), ops.element(), etc."""

import os
import sys
import types


class Model:
    """A mock replacement for openseespy.opensees that records model data
    instead of building a real OpenSees model.
    """
    def __init__(self):
        self.nodes = []
        self.elements = []
        self.fixities = []
        self.ndm = 2

    def model(self, *args):
        args = [str(a) for a in args]
        if '-ndm' in args:
            idx = args.index('-ndm')
            self.ndm = int(args[idx + 1])

    def node(self, tag, *coords):
        self.nodes.append((int(tag),) + tuple(float(c) for c in coords))

    def element(self, etype, tag, iNode, jNode, *rest):
        self.elements.append((str(etype), int(tag), int(iNode), int(jNode)))

    def fix(self, tag, *dofs):
        self.fixities.append((int(tag),) + tuple(int(d) for d in dofs))

    def __getattr__(self, name):
        # Catch-all: silently ignore any other ops.xxx() call
        return lambda *args, **kwargs: None


def parse_py(pyfiles):
    """Parse OpenSeesPy (.py) files by mocking the openseespy module and
    executing the user's script. All ops.node/element/fix calls are recorded.
    Returns (nodes, elements, fixities, ndm).
    """
    mock = Model()

    mock_package = types.ModuleType('openseespy')
    mock_package.opensees = mock
    mock_package.__path__ = []

    saved = {}
    for key in ('openseespy', 'openseespy.opensees'):
        if key in sys.modules:
            saved[key] = sys.modules[key]

    sys.modules['openseespy'] = mock_package
    sys.modules['openseespy.opensees'] = mock

    try:
        for pyfile in pyfiles:
            filepath = os.path.abspath(pyfile)
            with open(filepath, 'r') as f:
                code = f.read()
            exec(compile(code, filepath, 'exec'),
                 {'__name__': '__main__', '__file__': filepath})
    except Exception as e:
        print(f'Error parsing {pyfile}: {e}')
    finally:
        for key in ('openseespy', 'openseespy.opensees'):
            if key in saved:
                sys.modules[key] = saved[key]
            elif key in sys.modules:
                del sys.modules[key]

    return mock.nodes, mock.elements, mock.fixities, mock.ndm
