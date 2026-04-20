"""
Runtime hook: stub out torch._dynamo in frozen builds.

torchvision.ops.roi_align does `import torch._dynamo` at module level,
which triggers the import chain:
    torch._dynamo -> torch._dynamo.utils -> torch._numpy -> torch._numpy._ufuncs
The _ufuncs module uses a vars()[name] pattern that crashes in frozen builds
(NameError: name 'name' is not defined).

torch lazily loads _dynamo via __getattr__, so pre-populating sys.modules
with a minimal stub prevents the real module from ever loading.
This app only runs model inference (torch.no_grad()), so _dynamo's JIT
compilation features are never actually needed.

Attributes provided:
  - allow_in_graph: no-op decorator (used by torchvision.ops.roi_align)
  - is_compiling: returns False (used by torchvision.transforms.v2)
  - disable / optimize: no-op decorators (used by torch.compile paths)
"""
import sys
import types

_stub = types.ModuleType("torch._dynamo")
_stub.allow_in_graph = lambda fn: fn
_stub.is_compiling = lambda: False
_stub.disable = lambda fn=None, **kw: (lambda f: f) if fn is None else fn
_stub.optimize = lambda fn=None, **kw: (lambda f: f) if fn is None else fn

sys.modules["torch._dynamo"] = _stub
