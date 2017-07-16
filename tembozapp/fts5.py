def fts5_term(term):
  """Convert a Google search like query into a FTS5 query, i.e. to not
  trigger the column filter misfeature. We don't try to make invalid queries
  work, just make queries that would be interpreted as column filters or the
  like work.

  EBNF:
  query = word
  word = [not space]+
  query = phrase
  phrase = '"' [^"]* '"'
  query = "(" query ")"
  query = query "AND" query
  query = query "OR" query
  query = "NOT" query
  """
  in_q = False
  implicit_q = False
  out = []
  expect = None
  pending = []
  for c in term:
    if c == "'": # SQL injection guard
      if pending:
        out.extend(pending)
        pending = None
      out.append("''")
    elif expect:
      if c != expect:
        assert not in_q
        out.append('"')
        out.extend(pending)
        out.append('"')
        out.append(c)
        expect = None
        pending = None
      else:
        pending.append(c)
        expect = {'N': 'D', 'D': None, 'R': None, 'O': 'T', 'T': None}[expect]
        if expect is None:
          assert not in_q
          out.extend(pending)
          expect = None
          pending = None
    elif c == '"':
      if implicit_q:
        implicit_q = False
      else:
        in_q = not in_q
        out.append(c)
    elif not in_q and c in 'AON':
      expect = {'A': 'N', 'O': 'R', 'N': 'O'}[c]
      pending = [c]
    elif c in ' \t\n()':
      if implicit_q:
        out.append('"')
        implicit_q = False
        in_q = False
      out.append(c)
    else:
      if in_q:
        out.append(c)
      else:
        in_q = True
        implicit_q = True
        out.append('"')
        out.append(c)
  if pending:
    out.extend(pending)
  if in_q:
    out.append('"')
  return ''.join(out)

if __name__ == '__main__':
  for input, expected in [
      ('foo', '"foo"'),
      ('foo bar', '"foo" "bar"'),
      ('"foo"', '"foo"'),
      ('"foo bar"', '"foo bar"'),
      ('foo AND bar', '"foo" AND "bar"'),
      ('(foo AND bar) OR baz', '("foo" AND "bar") OR "baz"'),
      ('foo AN bar', '"foo" "AN" "bar"'),
      ('"foo AN bar"', '"foo AN bar"'),
  ]:
    out = fts5_term(input)
    assert out == expected, \
      'input=%r expected=%r got=%r' % (input, expected, out)
