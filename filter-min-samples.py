#! /usr/bin/env python
"""
Filter hashes in FracMinHash sketches for presence in minimum number of
samples.

Supports the full range of sourmash output formats per

https://sourmash.readthedocs.io/en/latest/command-line.html#choosing-signature-output-formats

For integration into sourmash sig commonhash or occurrence,
* support full range of moltypes
* support max samples, too
"""
import sys
import argparse
import sourmash
from sourmash import sourmash_args
from collections import Counter


def main():
    p = argparse.ArgumentParser()
    p.add_argument('sigfiles', nargs='+')
    p.add_argument('-k', '--ksize', default=31, type=int)
    p.add_argument('-o', '--output', required=True)
    p.add_argument('-m', '--min-samples', default=2, type=int)
    args = p.parse_args()

    print(f"Selecting k={args.ksize}, DNA")

    # first pass: count number of samples for each hash
    all_hashes = Counter()
    n_signatures = 0
    for filename in args.sigfiles:
        db = sourmash.load_file_as_index(filename)
        db = db.select(ksize=args.ksize, moltype='DNA')

        for ss in db.signatures():
            # note: flatten => count each hash only once,
            # independent of abundance
            flat_mh = ss.minhash.flatten()
            all_hashes.update(flat_mh.hashes)

            n_signatures += 1

    print(f"Loaded {len(all_hashes)} hashes from {n_signatures} sketches in {len(args.sigfiles)} files.")

    # find all hashes with abundance >= min_samples
    keep_hashes = set()
    min_samples = args.min_samples
    for hashval, v in all_hashes.items():
        # filter on minimum number of samples
        if v >= min_samples:
            keep_hashes.add(hashval)

    print(f'Of {len(all_hashes)} hashes, keeping {len(keep_hashes)} that are in {min_samples} or more samples.')

    save_sigs = sourmash_args.SaveSignaturesToLocation(args.output)
    save_sigs.open()

    # second pass: filter!
    for filename in args.sigfiles:
        db = sourmash.load_file_as_index(filename)
        db = db.select(ksize=args.ksize, moltype='DNA')

        for ss in db.signatures():
            mh = ss.minhash
            new_mh = mh.copy_and_clear()
            keep_these_hashes = keep_hashes.intersection(mh.hashes)

            # retain abundance, if present; else just add hashes.
            if mh.track_abundance:
                for hashval in keep_these_hashes:
                    abund = mh.hashes[hashval]
                    new_mh.add_hash_with_abundance(hashval, abund)
            else:
                new_mh.add_many(keep_these_hashes)

            new_ss = sourmash.SourmashSignature(new_mh, name=ss.name)

            save_sigs.add(new_ss)

    save_sigs.close()

    print(f"Saved {len(save_sigs)} signatures to '{args.output}'")


if __name__ == '__main__':
    sys.exit(main())
