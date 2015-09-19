#!/usr/bin/env python

"""Parse, summarize, and upload a Valgring callgrind file to New Relic."""

# Just a first incrementally parsing some Valgrind callgrind file format
# using the PLY module (the Natural Language Toolkit, NLTK, is also
# another possibility)

import sys
import ply.lex as lex
import ply.yacc as yacc   # pylint: disable=unused-import

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
#
#     TargetCommand := "cmd:" Space* NoNewLineChar*
#
#     TargetID := ("pid"|"thread"|"part") ":" Space* Number
#
#     Description := "desc:" Space* Name Space* ":" NoNewLineChar*
#
#     EventSpecification := "event:" Space* Name InheritedDef? LongNameDef?
#
#     CostLineDef := "events:" Space* Name (Space+ Name)*
#
#     Name = Alpha (Digit | Alpha)*
#


class PlyLexerValgrindCallgrind(object):
    """A class whose instantations will have the PLY lexer for the Valgrind
    Callgrind file format.

    This lexer is being built incrementally, adding new tokens from the
    Callgrind grammar specification. The YACC parser for the Context-Free
    Grammar will be built later.
    """

    def __init__(self):
        """Instance constructor"""
        self.lexer = lex.lex(module=self)

    def tokenize_strings(self, strings):
        """tokenize strings"""
        self.lexer.input(strings)
        while True:
            token = self.lexer.token()
            if not token:
                break
            print token
        return True

    # Ignored characters
    # t_ignore = " \t"

    # Order is important in the tokens in PLY for it is the order in which
    # the tokens will be analyzed, eg., the possibility of token
    #             'lex_hex_number'
    # should should be analyzed before the possibility of the token
    #             'lex_dec_number'
    # and similarly, the possibility of token
    #             'lex_name'
    # should be analyzed before token
    #             'lex_rest_of_line'

    tokens = (
        'lex_hex_number', 'lex_dec_number', 'lex_new_line',
        'lex_version', 'lex_creator', 'lex_target_command',
        'lex_target_id_pid', 'lex_target_id_thread', 'lex_target_id_part',
        'lex_description', 'lex_event_specification', 'lex_call_line_calls',
        'lex_name', 'lex_rest_of_line', 'lex_spacetab'
    )

    # Tokens
    # We mostly define the PLY tokens not as PLY regular-expression objects,
    # but PLY functions, since the later give more flexibility

    def t_lex_hex_number(self, lex_token):  # pylint: disable=no-self-use
        r'0x[0-9A-Fa-f]+'
        try:
            lex_token.value = int(lex_token.value, 16)
        except ValueError:
            print "Hexadecimal value too large %x", lex_token.value
            lex_token.value = 0
        return lex_token

    def t_lex_dec_number(self, lex_token):  # pylint: disable=no-self-use
        r'\d+'
        try:
            lex_token.value = int(lex_token.value)
        except ValueError:
            print "Integer value too large %d", lex_token.value
            lex_token.value = 0
        return lex_token

    def t_lex_new_line(self, lex_token):  # pylint: disable=no-self-use
        r'\n'
        lex_token.lexer.lineno += 1

    def t_lex_version(self, lex_token):  # pylint: disable=no-self-use
        r'(?m)^[ \t]*version:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_creator(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*creator:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_command(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*cmd:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_id_pid(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*pid:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_id_thread(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*thread:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_id_part(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*part:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_description(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*desc:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_event_specification(self, lex_token):  # pylint: disable=no-self-use
        '(?m)^[ \t]*event:'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_call_line_calls(self, lex_token):  # pylint: disable=no-self-use
        r'(?m)^[ \t]*calls='
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_name(self, lex_token):  # pylint: disable=no-self-use
        '[a-zA-Z][a-zA-Z0-9]*'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_rest_of_line(self, lex_token):  # pylint: disable=no-self-use
        r'.+'
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_spacetab(self, dummy_token):  # pylint: disable=no-self-use
        r'\s'
        # Adding this function which allows the line-oriented nature of the
        # Callgrind, like:
        #    ^[ \t]*version: ... <line> ... '\n'
        #    ^[ \t]*creator: ... <line> ... '\n'
        # ie., the Callgrind records are VERY line oriented (they can't wrap
        # to the next line), and this function allows t_lex_spacetab() allows
        # to do this (see:
        # http://stackoverflow.com/questions/23925820/python-lex-yaccply-not-recognizing-start-of-line-or-start-of-string
        # )
        pass

    def t_error(self, lex_token):  # pylint: disable=no-self-use
        # pylint: disable=missing-docstring
        print "Illegal character '%s'" % lex_token.value[0]
        lex_token.lexer.skip(1)


def main():
    """Main function."""

    # this is a simple test of the current state of the lexer on a callgrind
    # file
    callgrind_input_file = "test.callgrind"
    if len(sys.argv) >= 2:
        callgrind_input_file = sys.argv[1]

    with open(callgrind_input_file, "r") as callgrind_file:
        data = callgrind_file.read()

    callgrind_lexer = PlyLexerValgrindCallgrind()
    callgrind_lexer.tokenize_strings(data)


if __name__ == '__main__':
    main()
