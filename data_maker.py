#! /usr/bin/env python3

# Copyright 2017 Pilosa Corp.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.


import argparse
import random
import sys
import time

"""
Sample usage: python3 data_maker.py -r 5000 -c 5000 -f '0.3 < random.gauss(mu=0.5, sigma=0.4) < 0.6' > index-frame1_5000x5000.csv
"""


def generate(row_count, column_count, fun):
    for row in range(row_count):
        for col in range(column_count):
            if fun(row, col, row_count, column_count):
                yield u"%s,%s" % (row, col)


def random_bit(clamp_low=0.0, clamp_high=1.0, fun=random.random):
    return lambda row, col, row_count, column_count: clamp_low <= fun() <= clamp_high


def estimate_density(fun):
    bit_counts = []
    run_count = 5
    row_count = 100
    column_count = 100
    for i in range(run_count):
        bit_counts.append(len(list(generate(row_count, column_count, fun))))
    return sum(bc / (row_count*column_count) for bc in bit_counts) / run_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rows", help="row count", type=int)
    parser.add_argument("-c", "--columns", help="column count", type=int)
    parser.add_argument("-f", "--function", help="function")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--dry-run", action='store_true')
    args = parser.parse_args()
    if not (args.rows or args.columns or args.function):
        parser.error("rows, columns and function arguments are required")
    seed = args.seed or int(time.time() * 1000000)
    print("Seed:", seed, file=sys.stderr)
    random.seed(seed)
    bit_count = 0
    fun = eval("lambda r, c, nr, nc: %s" % args.function)

    if args.dry_run:
        estimated_density = estimate_density(fun)
        print("Estimated bit count: {:,}".format(int(args.rows * args.columns * estimated_density)))
        print("Estimated density:", estimated_density)
        sys.exit(0)

    for line in generate(args.rows, args.columns, fun):
        print(line)
        bit_count += 1
    print("Bit count: {:,}".format(bit_count), file=sys.stderr)
    print("Density:", bit_count / (args.rows * args.columns), file=sys.stderr)


if __name__ == '__main__':
    main()

