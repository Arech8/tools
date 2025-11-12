# Some useful tools and snippets for work with AMD software stack

1. [ROCTx](./ROCTx) is a custom bindings for Python for ROCTx trace/profile annotation C-library.
2. [AMD_LOG_LEVEL_FILE dethreader](./AMD_LOG_LEVEL_FILE-dethreader) is a script to split a single
AMD_LOG_LEVEL log file into a set of process/thread-specific files.
3. [bpftrace_tracer](./bpftrace_tracer) is a code for a custom `bpftrace`-based tracer I built to
debug an extremely latency sensitive hang. It's essentially a singleuse code, but it can be repurposed
to solve a similar problem.
