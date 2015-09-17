#!/usr/bin/env python

#pylint: skip-file
#
# Just a first incrementally parsing some Valgrind callgrind file format
# using the PLY module (the Natural Language Toolkit, NLTK, is also
# another possibility)

import ply.lex as lex
import ply.yacc as yacc

# An incremental test of some productions in the grammar (and associated
# lexical tokens)
#
# http://valgrind.org/docs/manual/cl-format.html#cl-format.reference.grammar
#
#     ProfileDataFile := FormatVersion? Creator? PartData*
#
#     FormatVersion := "version:" Space* Number "\n"
#
#     Creator := "creator:" NoNewLineChar* "\n"

# Ignored characters
t_ignore = " \t"

tokens = (
    'VERSION','DEC_NUMBER', 'HEX_NUMBER', 'NEWLINE',
    'CREATOR','REST_OF_LINE'
    )

# Tokens

t_VERSION    = r'version:'
t_CREATOR  = r'creator:'
t_REST_OF_LINE = r'.+'

def t_DEC_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Integer value too large %d", t.value 
        t.value = 0
    return t

def t_HEX_NUMBER(t):
    r'0x[0-9A-Fa-f]+'
    try:
        t.value = int(t.value, 16)
    except ValueError:
        print "Hexadecimal value too large %x", t.value 
        t.value = 0
    return t

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
lexer = lex.lex()

with open("test.callgrind","r") as callgrind_file:
    data = callgrind_file.read()

lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)

