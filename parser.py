#!/usr/bin/python

import sys

def find_comment(line):
    # Search for a comment in a line. If there is a comment, separate it out
    line = line.strip()
    in_quote = "" # If we are within quotes, what is the quote character
    quote_chars = ("'", '"') # The characters that we count as a quote

    comment = "" # The comment line to spit out
    result = "" # The code that is within the line to spit out

    # Loop through every character in the line
    for i in range(len(line)):
        ch = line[i] # The character at a given index
        # If we are not in a quote and we find a quote, set the quote character
        if ch in quote_chars and in_quote == "":
            in_quote = ch
        # We are already in a quote, so check if this closes it
        elif ch == in_quote:
            # TODO Do a real escape test.
            if i >= 1 and line[i-1] != "\\":
                in_quote = ""
        if ch == "#" and in_quote == "":
            result = line[:i] # the line is everything up until the #
            comment = line[i:] # the comment is everything after the #
            return result.strip(), comment.strip()
    result = line
    return result, "" # just return the entire line with no comment

for line in sys.stdin:
    print find_comment(line)





