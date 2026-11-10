#!/usr/bin/env python3
"""Regression test: re-importing an OPML file counts duplicates cleanly."""
import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.abspath(__file__))


class TestOpmlImport(unittest.TestCase):
  def test_duplicate_import_counts_dups(self):
    tmp = tempfile.mkdtemp()
    old = os.getcwd()
    os.chdir(tmp)
    try:
      con = sqlite3.connect('rss.db')
      with open(os.path.join(REPO, 'tembozapp', 'ddl.sql'), encoding='utf-8') as f:
        con.executescript(f.read())
      con.commit()
      con.close()
      sys.path.insert(0, REPO)
      from tembozapp import opml
      src = os.path.join(REPO, 'test', 'subscriptionList.opml')
      buf = io.StringIO()
      with contextlib.redirect_stdout(buf):
        opml.import_opml(src)
        opml.import_opml(src)
      out = buf.getvalue()
      assert 'rejected as duplicates' in out, out
    finally:
      os.chdir(old)


if __name__ == '__main__':
  unittest.main()
