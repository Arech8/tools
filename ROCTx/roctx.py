from ctypes import cdll, c_int, c_char_p, c_uint64
from functools import wraps


# Context wrappers are snatched and modified from
# https://github.com/ROCm/rocprofiler-sdk/blob/72b97a8b7e8322e78314f8b9164b96bec7d1c044/source/lib/python/roctx/context_decorators.py#L30
class RoctxRange:
    """Provides decorators and context-manager for roctx range"""

    def __init__(self, R, msg:str=None):
        """Initialize with a message. R should have an interface of Roctx class, see below"""
        self.r = R
        self.msg = msg

    def __call__(self, func):
        """Decorator"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.r.rangePush(self.msg)
            try:
                return func(*args, **kwargs)
            finally:
                self.r.rangePop()

        return wrapper

    def __enter__(self):
        """Context manager start function"""
        if self.msg is not None:
            self.a = self.r.rangePush(self.msg)
            return self.a
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """Context manager stop function"""
        if self.msg is not None:
            self.r.rangePop()

        if exc_type is not None and exc_value is not None and tb is not None:
            import traceback

            traceback.print_exception(exc_type, exc_value, tb, limit=5)


class RoctxEnabler:
    """Provides decorators and context-manager for roctx profiler"""

    def __init__(self, R, tid=0):
        """Initialize with a tid. R should have an interface of Roctx class, see below"""
        self.r = R
        self.tid = tid

    def __call__(self, func):
        """Decorator"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.r.profilerResume(self.tid)
            try:
                return func(*args, **kwargs)
            finally:
                self.r.profilerPause(self.tid)

        return wrapper

    def __enter__(self):
        """Context manager start function"""
        self.a = self.r.profilerResume(self.tid)
        return self.a

    def __exit__(self, exc_type, exc_value, tb):
        """Context manager stop function"""

        self.r.profilerPause(self.tid)

        if exc_type is not None and exc_value is not None and tb is not None:
            import traceback

            traceback.print_exception(exc_type, exc_value, tb, limit=5)


class Roctx:
    """An interface to ROCTx.
    
    Here's how to import it without messing with PYTHONPATH, assuming that your
    current __file__ is 2 levels below a sibling of this repo root:

    def importRoctxHelper():
        import os
        import importlib

        mod_path = os.path.realpath(os.path.dirname(__file__) + "/../../tools/ROCTx/roctx.py")
        mod_name = os.path.splitext(os.path.basename(mod_path))[0].capitalize()
        spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        helper = getattr(module, mod_name)
        return helper # Roctx class
    RoctxHlpr = importRoctxHelper()
    roctx = RoctxHlpr(os.environ.setdefault("ARECH_TRACE", "0")) # instance of Roctx class
    # roctx.profilerPause()
    
    When the snippet is executed with environment variable ARECH_TRACE having a
    compatible value (1, or 2, or 3), roctx will be an working interface to
    ROCTx, otherwise it’ll be a mock interface.
    """
    Range = RoctxRange
    Enabler = RoctxEnabler

    def __init__(self, prof_ver=None, rocm_path=None):
        """Initializer.
        prof_ver: str|int - is a profiler version to be used, any of (1,2,3). Any other value
        disables all functionality (all functions are replaced by stubs with compatible API that do
        nothing). Version number affects on which implementation library is loaded. Version 3 has
        the most features"""
        if isinstance(prof_ver, str):
            prof_ver = int(prof_ver)

        if prof_ver in (1, 2, 3):
            if rocm_path is None:
                rocm_path = "/opt/rocm"

            if prof_ver == 3:
                lib_path = rocm_path + "/lib/librocprofiler-sdk-roctx.so"
            else:
                # API is restricted compared to sdk-roctx
                lib_path = rocm_path + "/lib/libroctx64.so"  

            print(f"Loading {lib_path}...")
            lib = cdll.LoadLibrary(lib_path)

            # See the docs at
            # https://github.com/ROCm/rocprofiler-sdk/blob/amd-staging/source/include/rocprofiler-sdk-roctx/roctx.h

            self.mark = lambda x: lib.roctxMarkA(x.encode("utf-8"))
            self.mark.argtypes = [c_char_p]
            self.mark.restype = None

            self.rangePush = lambda x: lib.roctxRangePushA(x.encode("utf-8"))
            self.rangePush.argtypes = [c_char_p]
            self.rangePush.restype = c_int

            self.rangePop = lib.roctxRangePop
            self.rangePop.restype = c_int

            self.rangeStart = lambda x: lib.roctxRangeStartA(x.encode("utf-8"))
            self.rangeStart.argtypes = [c_char_p]
            self.rangeStart.restype = c_uint64

            self.rangeStop = lib.roctxRangeStop
            self.rangeStop.argtypes = [c_uint64]
            self.rangeStop.restype = None

            if prof_ver == 3:
                self.profilerPause = lambda x=None: lib.roctxProfilerPause(
                    0 if x is None else x
                )
                self.profilerPause.argtypes = [c_uint64]
                self.profilerPause.restype = c_int

                self.profilerResume = lambda x=None: lib.roctxProfilerResume(
                    0 if x is None else x
                )
                self.profilerResume.argtypes = [c_uint64]
                self.profilerResume.restype = c_int
            else:
                self.profilerPause = lambda x=None: -1
                self.profilerResume = lambda x=None: -1

        else:
            print("Making fake Roctx interface")
            self.mark = lambda x: None
            self.rangePush = lambda x: -1
            self.rangePop = lambda: -1
            self.rangeStart = lambda x: -1
            self.rangeStop = lambda x: None
            self.profilerPause = lambda x=None: -1
            self.profilerResume = lambda x=None: -1
