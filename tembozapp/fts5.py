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
  WS = 'WORDSEP'
  #print('-'*72)
  #print(f'Parsing {term}')
  for c in term:
    #print(f'c={c} in_q={in_q} implicit_q={implicit_q} out={out} expect={expect} pending={pending}')
    if c == "'": # SQL injection guard
      if pending:
        if not implicit_q:
          out.append('"')
          implicit_q = True
        out.extend(pending)
        pending = None
      out.append("''")
      continue
    if expect:
      assert not in_q
      if expect == WS and c not in ' \t\n("' or expect != WS and c != expect:
        out.append('"')
        implicit_q = True
        out.extend(pending)
        expect = None
        pending = None
      elif expect == WS:
        out.extend(pending)
        expect = None
        pending = None
      else:
        pending.append(c)
        expect = {'N': 'D', 'D': WS, 'R': WS, 'O': 'T', 'T': WS}[expect]
        continue
    if c == '"':
      if implicit_q:
        implicit_q = False
        in_q = True
      else:
        in_q = not in_q
        out.append(c)
    elif not in_q and not implicit_q and c in 'AON':
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
      elif implicit_q:
        out.append(c)
      else:
        in_q = True
        implicit_q = True
        out.append('"')
        out.append(c)
  if pending:
    out.extend(pending)
  if in_q or implicit_q:
    out.append('"')
  return ''.join(out)

if __name__ == '__main__':
  fts5_term('foo AND bar')
  for input, expected in [
      ('foo', '"foo"'),
      ('foo bar', '"foo" "bar"'),
      ('"foo"', '"foo"'),
      ('"foo bar"', '"foo bar"'),
      ('foo AND bar', '"foo" AND "bar"'),
      ('(foo AND bar) OR baz', '("foo" AND "bar") OR "baz"'),
      ('foo AN bar', '"foo" "AN" "bar"'),
      ('"foo AN bar"', '"foo AN bar"'),
      ('ACME', '"ACME"'),
      ('Acme', '"Acme"'),
      ('OpenBSD', '"OpenBSD"'),
      ('ANAN', '"ANAN"'),
      ('ANAND', '"ANAND"'),
      ('AN"D"', '"AND"'),
      ('NOTAM', '"NOTAM"'),
      ('ANDROS', '"ANDROS"'),
  ]:
    out = fts5_term(input)
    assert out == expected, \
      'input=%r expected=%r got=%r' % (input, expected, out)
