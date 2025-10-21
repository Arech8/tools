"""
dethreader splits a single AMD_LOG_LEVEL log file into a set of thread-specific files

[`AMD_LOG_LEVEL`](https://rocm.docs.amd.com/projects/HIP/en/develop/how-to/debugging.html#hip-environment-variable-summary)
and [`AMD_LOG_LEVEL_FILE`](https://github.com/ROCm/clr/blob/a2550e0a9ecaa8f371cb14d08904c51874c37cbe/rocclr/utils/flags.hpp#L31)
environment variables provide a powerful way to sneak peek into the execution of
ROCm based programs.

One currently undocumented feature of `AMD_LOG_LEVEL` is that levels starting
from `4` [augment the log](https://github.com/ROCm/clr/blob/a2550e0a9ecaa8f371cb14d08904c51874c37cbe/rocclr/utils/debug.cpp#L99)
with the caller process' and thread' identifiers, which are super handy to
untangle multithreaded or even multiprocess mess that a real world software
produces. This script splits a single log file obtained with a such level into
a set of log files each corresponding to a unique pid/tid combination found in
the log, which makes analysing the log much easier.

A useful thing to note here, that experience tells that a parser of related
[`AMD_LOG_MASK`](https://github.com/ROCm/clr/blob/a2550e0a9ecaa8f371cb14d08904c51874c37cbe/rocclr/utils/debug.hpp#L47)
variable at least in ROCm 6.3.4 don't handle hexadecimal values properly, so if
you customize the mask - make sure to specify it a decimals.
"""

import argparse
import os
import re


kUntaggedPolicy = {"separate": 0, "as_previous": 1}


def makeCLIParser():
    parser = argparse.ArgumentParser(
        description="Splits a single AMD_LOG_LEVEL log file into a set of thread-specific files",
        # formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "src",
        help="Path to a combined log file to de-thread",
        metavar="<path/to/source_file>",
    )

    parser.add_argument(
        "--untagged",
        help="Sets how to deal with log lines that aren't tagged with pid/tid markers. "
        "Default is %(default)s. "
        f"Choices are: {', '.join(kUntaggedPolicy.keys())}",
        metavar="<policy_id>",
        choices=kUntaggedPolicy.keys(),
        default=next(iter(kUntaggedPolicy.keys())),
    )

    return parser


def dethread(src_file: str, untagged_policy: str = next(iter(kUntaggedPolicy.keys()))):
    untagged_policy = untagged_policy.lower()
    assert untagged_policy in kUntaggedPolicy
    assert len(kUntaggedPolicy) == 2
    kPolicyIsSeparate = untagged_policy == "separate"

    # first group ends on a timestamp right before [pid ...] section
    matcher = re.compile(
        r"^(.*?s\:\s)(\[pid:\s*(\d+)\s+tid:\s*(?:0x)?([\da-fA-F]+)\]\s*)(.*)$"
    )
    log = {}  # pid->tid->[entries...]
    last_pid, last_tid = -1, -1

    total_lines=0

    with open(src_file, "r") as file:
        for line in file:
            total_lines +=1
            m = matcher.match(line)
            if m:
                matches = m.groups()
                assert 5 == len(matches), f"5 groups expected, found {len(matches)}"
                assert all(e is not None for e in matches), "Not all groups had a match"
                spid, stid = matches[2], matches[3]
                pid, tid = int(spid), int(stid, base=16)
                last_pid, last_tid = pid, tid
                entry = m.expand("\\1\\5")
            else:
                entry = line.rstrip()
                if kPolicyIsSeparate:
                    pid, tid = -1, -1
                else:
                    pid, tid = last_pid, last_tid

            ptlog = log.setdefault(pid, {}).setdefault(tid, [])
            ptlog.append(entry)

    print(f"Read {total_lines} lines from {src_file}. There are up to {len(log)} processes.")

    fdir,fname = os.path.split(src_file)
    for pid, tids in log.items():
        for tid, entries in tids.items():
            print(f"pid {pid}, tid={tid:08x} has {len(entries)} entries")
            total_lines -= len(entries)
            with open(f"{fdir}/pid={pid}_tid={tid:08x}_{fname}","w") as f:
                f.write("\n".join(entries))
    assert 0 ==total_lines, "WTF?"

def main():
    parser = makeCLIParser()
    args = parser.parse_args()
    dethread(args.src, args.untagged)


if __name__ == "__main__":
    main()
