#!/usr/bin/env python

"""
Parse the grammar, summarize the syntactic tree, and upload a Valgring
callgrind file to New Relic.
"""

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
#     CostPosition := "ob" | "fl" | "fi" | "fe" | "fn"
#
#     CalledPosition := " "cob" | "cfi" | "cfl" | "cfn"
#


class PlyLexerValgrindCallgrind(object):
    # pylint: disable=too-many-public-methods
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
        'lex_equal_sign', 'lex_hex_number', 'lex_dec_number', 'lex_new_line',
        'lex_version', 'lex_creator', 'lex_target_command',
        'lex_target_id_pid', 'lex_target_id_thread', 'lex_target_id_part',
        'lex_description', 'lex_event_specification', 'lex_call_line_calls',
        'lex_cost_line_def_events', 'lext_cost_position_ob',
        'lext_cost_position_fl', 'lext_cost_position_fi',
        'lext_cost_position_fe', 'lext_cost_position_fn',
        'lex_called_position_cob', 'lex_called_position_cfi',
        'lex_called_position_cfl', 'lex_called_position_cfn',
        'lex_name', 'lex_rest_of_line', 'lex_spacetab'
    )

    # Tokens
    # We mostly define the PLY tokens not as PLY regular-expression objects,
    # but PLY functions, since the later give more flexibility

    def t_lex_equal_sign(self, lex_token):
        r'='
        # pylint: disable=no-self-use
        return lex_token

    def t_lex_hex_number(self, lex_token):
        r'0x[0-9A-Fa-f]+'
        # pylint: disable=no-self-use
        try:
            lex_token.value = int(lex_token.value, 16)
        except ValueError:
            print "Hexadecimal value too large %x", lex_token.value
            lex_token.value = 0
        return lex_token

    def t_lex_dec_number(self, lex_token):
        r'\d+'
        # pylint: disable=no-self-use
        try:
            lex_token.value = int(lex_token.value)
        except ValueError:
            print "Integer value too large %d", lex_token.value
            lex_token.value = 0
        return lex_token

    def t_lex_new_line(self, lex_token):
        r'\n'
        # pylint: disable=no-self-use
        lex_token.lexer.lineno += 1

    def t_lex_version(self, lex_token):
        r'(?m)^[ \t]*version:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_creator(self, lex_token):
        '(?m)^[ \t]*creator:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_command(self, lex_token):
        '(?m)^[ \t]*cmd:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_id_pid(self, lex_token):
        '(?m)^[ \t]*pid:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_id_thread(self, lex_token):
        '(?m)^[ \t]*thread:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_target_id_part(self, lex_token):
        '(?m)^[ \t]*part:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_description(self, lex_token):
        '(?m)^[ \t]*desc:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_event_specification(self, lex_token):
        '(?m)^[ \t]*event:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_call_line_calls(self, lex_token):
        r'(?m)^[ \t]*calls'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_cost_line_def_events(self, lex_token):
        r'(?m)^[ \t]*events:'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lext_cost_position_ob(self, lex_token):
        r'(?m)^[ \t]*ob'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lext_cost_position_fl(self, lex_token):
        r'(?m)^[ \t]*fl'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lext_cost_position_fi(self, lex_token):
        r'(?m)^[ \t]*fi'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lext_cost_position_fe(self, lex_token):
        r'(?m)^[ \t]*fe'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lext_cost_position_fn(self, lex_token):
        r'(?m)^[ \t]*fn'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_called_position_cob(self, lex_token):
        r'(?m)^[ \t]*cob'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_called_position_cfi(self, lex_token):
        r'(?m)^[ \t]*cfi'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_called_position_cfl(self, lex_token):
        r'(?m)^[ \t]*cfl'
        # pylint: disable=no-self-use
        lex_token.value = lex_token.value.strip()
        return lex_token

    def t_lex_called_position_cfn(self, lex_token):
        r'(?m)^[ \t]*cfn'
        # pylint: disable=no-self-use
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
