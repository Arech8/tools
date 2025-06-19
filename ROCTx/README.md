# Custom ROCTx Python bindings (system profiler/tracer annotations for Python)

First: there exist an [official Python package](https://rocm.docs.amd.com/projects/rocprofiler-sdk/en/amd-mainline/how-to/using-rocprofiler-sdk-roctx.html#using-roctx-in-the-python-application) for ROCTx, consider first if you can/want to use it. Note that they don't say this in docs, but even if your `import roctx` fails, ensure that `/opt/rocm/lib/python<your_version_here>/site-packages` is your `PYTHONPATH`.

Second: this is an alternative Python bindings for ROCTx that use a corresponding ROCTx C-library directly when you needed it, or provide an empty mock interface when you don't. Read the code for the details, it's tiny and trivially simple. Also there's a suggested way to import the implementation class without messing with `PYTHONPATH`.



