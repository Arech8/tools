# AMD_LOG_LEVEL_FILE-dethreader splits a single log file into a set of thread-specific files

[`AMD_LOG_LEVEL`](https://rocm.docs.amd.com/projects/HIP/en/develop/how-to/debugging.html#hip-environment-variable-summary) / [`AMD_LOG_LEVEL_FILE`](https://github.com/ROCm/clr/blob/a2550e0a9ecaa8f371cb14d08904c51874c37cbe/rocclr/utils/flags.hpp#L31) environment variables provide a powerful way to sneak peek into the execution of ROCm based programs.

One currently undocumented feature of `AMD_LOG_LEVEL` is that levels starting from `4` [augment the log](https://github.com/ROCm/clr/blob/a2550e0a9ecaa8f371cb14d08904c51874c37cbe/rocclr/utils/debug.cpp#L99) with the caller process' and thread' identifiers, which are super handy to untangle multithreaded or even multiprocess mess that a real world software produces. This script splits a single log file obtained with a such level into a set of log files each corresponding to a unique pid/tid combination found in the log, which makes analysing the log much easier.

A useful thing to note here, that experience tells that a parser of related [`AMD_LOG_MASK`](https://github.com/ROCm/clr/blob/a2550e0a9ecaa8f371cb14d08904c51874c37cbe/rocclr/utils/debug.hpp#L47) variable at least in ROCm 6.3.4 don't handle hexadecimal values properly, so if you customize the mask - make sure to specify it a decimals.
