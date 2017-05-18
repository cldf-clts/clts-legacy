# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import OrderedDict
import argparse
import unicodedata

from six import text_type
from clldutils.clilib import ArgumentParser, ParserError, command
from clldutils.path import Path
from clldutils.dsv import UnicodeWriter
from clldutils.markup import Table

from pyclpa.wordlist import Wordlist
from pyclpa.base import get_clpa


def _checked_wordlist_from_args(args):
    if len(args.args) != 1:
        raise ParserError('no input file specified')

    fname = Path(args.args[0])
    if not fname.exists():
        raise ParserError('invalid input file specified')

    wordlist = Wordlist.from_file(fname, delimiter=args.delimiter)
    segments = wordlist.check(column=args.column)
    return wordlist, segments


@command()
def annotate(args):
    """
    Will add two columns CLPA_TOKENS and CLPA_IDS to the input file.

    clpa annotate <FILE>

    Note
    ----

    * Rules point to a tab-separated value file in which source and target are
      given to convert a segment to another segment to be applied on a
      data-set-specific basis which may vary from dataset to dataset and can thus
      not be included as standard clpa behaviour.
    * Input file needs to be in csv-format with header, delimiter and name of the
      relevant column can be specified as --delimiter and --column options respectively.
    * The resulting CSV is printed to <stdout> or to the file specified as --output.

    """
    wordlist, _ = _checked_wordlist_from_args(args)
    res = wordlist.write(args.output)
    if args.output is None:
        print(res)


@command()
def report(args):
    """
    clpa report <FILE>

    Note
    ----

    * Rules point to a tab-separated value file in which source and target are
      given to convert a segment to another segment to be applied on a
      data-set-specific basis which may vary from dataset to dataset and can thus
      not be included as standard clpa behaviour.
    * Input file needs to be in csv-format with header, delimiter and name of the
      relevant column can be specified as --delimiter and --column options respectively.
    * format now allows for md (MarkDown), csv (CSV, tab as separator), or cldf
      (no pure cldf but rather current lingpy-csv-format). CLDF format means
      that the original file will be given another two columns, one called
      CLPA_TOKENS, one called CLPA_IDS.
    * The report is printed to <stdout> or to the file specified as --output.

    """
    wordlist, sounds = _checked_wordlist_from_args(args)

    segments = OrderedDict([('existing', []), ('missing', []), ('convertible', [])])

    for s in sounds:
        if s.clpa is None:
            type_ = 'missing'
        elif s.origin == s.clpa:
            type_ = 'existing'
        else:
            type_ = 'convertible'
        segments[type_].append([s.origin, s.clpa or '', s.frequency])

    if args.format == 'csv':
        with UnicodeWriter(args.output, delimiter='\t') as writer:
            for key, items in segments.items():
                for i, item in enumerate(items):
                    writer.writerow([i + 1] + item + [key])
        if args.output is None:
            print(writer.read())
        return

    res = []
    for key, items in segments.items():
        sounds = Table('number', 'sound', 'clpa', 'frequency')
        for i, item in enumerate(items):
            sounds.append([i + 1] + item)
        res.append('\n# {0} sounds\n\n{1}'.format(
            key.capitalize(), sounds.render(condensed=False)))
    res = '\n'.join(res)
    if args.output:
        with Path(args.output).open('w', encoding='utf8') as fp:
            fp.write(res)
    else:
        print(res)


@command()
def check(args):
    """
    clpa check <STRING>
    """
    if len(args.args) != 1:
        raise ParserError('only one argument allowed')
    clpa = get_clpa()
    seq = args.args[0]
    if not isinstance(seq, text_type):
        seq = seq.decode('utf8')  # pragma: no cover
    print('\t'.join(seq.split(' ')))
    print(clpa(unicodedata.normalize('NFC', seq), text=True).replace(' ', '\t'))


def main(args=None):
    parser = ArgumentParser('pyclpa', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-d", "--delimiter",
        help="Delimiting character of the input file.\n(default: <tab>)",
        default="\t")
    parser.add_argument(
        "-o", "--output",
        help="Output file.",
        default=None)
    parser.add_argument(
        "-c", "--column",
        help="Delimiting character of the input file.\n(default: TOKENS)",
        default="TOKENS")
    parser.add_argument(
        "--format",
        help="Output format for the report.\n(default: md)",
        choices=['md', 'csv', 'cldf'],
        default="md")

    res = parser.main(args=args)
    if args is None:  # pragma: no cover
        sys.exit(res)
