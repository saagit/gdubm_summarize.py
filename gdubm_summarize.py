#!/usr/bin/env python3

"""Outputs information from a Gnome Disk Utility benchmark cache file."""

# BSD Zero Clause License
#
# Copyright (c) 2024 Scott A. Anderson
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import argparse
import datetime
import sys
from gi.repository import GLib

def read_variant_from_benchmark_file(filename):
    """Return the GLib.Variant from the benchmark cache named <filename>."""

    mapped_file = GLib.MappedFile(filename, False)
    variant_type = GLib.VariantType('a{sv}')
    variant = GLib.Variant.new_from_bytes(variant_type, mapped_file.get_bytes(),
                                      False)
    assert variant['version'] == 1

    return variant

def average_of_samples(samples):
    """Return the average of the values (second tuple) from <samples>."""
    values = [sample[1] for sample in samples]
    return sum(values) / len(values)

def print_benchmark_summary(filename, variant):
    """Print a summary of information à la Gnome Disk Utility Benchmark."""

    print(f'{filename}:')

    print(f'{"Disk or Device":>22}  '
          f'{variant["device-size"]:,} bytes')

    last_time = datetime.datetime.fromtimestamp(variant["timestamp-usec"] / 1e6,
                                                datetime.timezone.utc)
    print(f'{"Last Benchmarked":>22}  '
          f'{last_time.strftime("%c %Z")}')

    print(f'{"Sample Size":>22}  '
          f'{variant["sample-size"]:,} bytes')

    print(f'{"Average Read Rate":>22}  '
          f'{average_of_samples(variant["read-samples"]) / 1e6:.1f} MB/s '
          f'({len(variant["read-samples"])} samples)')

    print(f'{"Average Write Rate":>22}  '
          f'{average_of_samples(variant["write-samples"]) / 1e6:.1f} MB/s '
          f'({len(variant["write-samples"])} samples)')

    print(f'{"Average Access Time":>22}  '
          f'{average_of_samples(variant["access-time-samples"]) * 1e3:.2f} msec '
          f'({len(variant["access-time-samples"])} samples)')

def print_benchmark_averages(filename, variant):
    """Print the read rate, write rate, access time averages and filename."""
    print(f'{round(average_of_samples(variant["read-samples"]))}\t'
          f'{round(average_of_samples(variant["write-samples"]))}\t'
          f'{average_of_samples(variant["access-time-samples"]):.6f}\t'
          f'{filename}')

def main():
    """The main event."""

    argp = argparse.ArgumentParser()
    argp.add_argument('-t', '--tsv', action='store_true',
                      help='Print the averages and filename separated by tabs.')
    argp.add_argument('benchmark_cache_files', nargs='+',
                      help='Benchmark cache file created by Gnome Disk Utility')
    args = argp.parse_args()

    for filename in args.benchmark_cache_files:
        variant = read_variant_from_benchmark_file(filename)
        if args.tsv:
            print_benchmark_averages(filename, variant)
        else:
            print_benchmark_summary(filename, variant)

    return 0

if __name__ == "__main__":
    sys.exit(main())
