#!/usr/bin/python

import sys, termcolor
from termcolor import colored

class QUOTES:
    def __init__(self):
        self.count = 0
        self.quotes = {}
    def add_quote(self, text, char='"'):
        quote_id = "__QUOTE_{}__".format(self.count)
        self.count += 1
        self.quotes[quote_id] = (char,text)
        return quote_id

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

def remove_quotes(QUOTE_MANAGER, line):
    # Remove all the quotes in the line and replace them with a unique ID
    line = line.strip()
    quote_start = 0
    quote_char = "" # character that we are searching for if we are in a quote
    quote_chars = ("'", '"') # The characters that we count as a quote

    output_line = []
    # Loop through every character in the line
    for i in range(len(line)):
        ch = line[i] # The character at a given index
        # If we are not in a quote and we find a quote, set the quote character
        if ch in quote_chars and quote_char == "":
            output_line += [line[quote_start:i]]
            quote_char = ch
            quote_start = i
        # We are already in a quote, so check if this closes it
        elif ch == quote_char:
            # TODO Do a real escape test.
            if i >= 1 and line[i-1] != "\\":
                quote_id = QUOTE_MANAGER.add_quote(line[quote_start+1:i],
                    quote_char)
                output_line += [quote_id]
                quote_char = ""
                quote_start = i+1
    output_line += [line[quote_start:]]
    return output_line

def add_semicolon(line):
    """
    Adds a semi colon if the line needs it
    line: (str) line to check
    return: (list) list of each line
    """
    retval = []
    line = line.strip()
    if line[0] == "#":
        # If its a comment, just skip the rest of the parsing
        return [line]
    words = line.split()
    # return nothing if there are no words
    if not words or len(line) == 0:
        return []

    # Words to check in the beginning to avoid
    end_words = ["do", "then", "else", "in"]
    # Defaul to adding a semicolon
    add = True
    # Check if the line ends in one of these words
    for w in end_words:
        # if there is an echo before, dont worry about it
        if w == words[-1] and "echo" not in words:
            add = False
            
    if line[-1] in (";", "{", "(", ")"):
        add = False
    
    if add:
        line = line + ";"
    return [line]

def split_brackets(line):
    line = line.strip()
    if "{" in line and "()" in line:
        if line.index("()") < line.index("{"):
            line = line.replace("{","\n{\n")
    return [ l.strip() for l in line.split("\n") if l != "" ]

def strip_comments(line):
    retval = []
    pos = -1
    if "#" in line:
        pos = line.index("#")
        retval += [line[pos:].strip()]
        retval += [line[:pos].strip()]
    else:
        retval += [line.strip()]
    return retval

def retab(lines):
    # Spaces for tabs
    tab_value = "    "
    tab_level = 0
    result = []
    tab_inc = ["do", "then", "{", "else", "elif"]
    tab_dec = ["fi;", "done;", "};", "else", "esac;", "elif"]
    for l in lines:
        words = l.split()
        for dec in tab_dec:
            if words[0] == dec:
                tab_level -= 1
        # Add the tabs to the level
        l = tab_value*tab_level + l
        # Have a special case for "in"
        if words[-1] == "in":
            tab_level += 1
        for inc in tab_inc:
            if words[0] == inc:
                tab_level += 1
        result += [l]
        
    return result


QUOTE_MANAGER = QUOTES()

if len(sys.argv) < 2:
    print "Usage "+__file__+" <filename>"
    quit()

# open the file and start processing the lines
with open(sys.argv[1]) as fil:
    # Remove all the quotes in the string
    lines = remove_quotes(QUOTE_MANAGER, fil.read())
    # condense all the lines into a single line
    lines = "".join(lines)
    # Substitute the switch end character so we can parse end lines
    lines = lines.replace(";;", "__CASE_SPECIAL_CHAR__")
    # Get each command separated on a new line
    lines = lines.replace(";", ";\n")
    # Clean up brackets
    
    # Replace the special character back into it
    lines = lines.replace("__CASE_SPECIAL_CHAR__", "\n;;\n")   
    # Separate each command into a new line
    lines = lines.split("\n")
    # remove excess space from each line
    lines = [ " ".join(l.split()) for l in lines ]
    # Strip whitespace from the lines
    lines = [ l.strip() for l in lines ]
    lines = filter(None, lines)
    
    # Strip all the comments
    new_lines = []
    for i in lines:
        new_lines += strip_comments(i)
    lines = []
    
    # Split any brackets for formating reasons
    for i in new_lines:
        lines += split_brackets(i)
    
    new_lines = []
    # Add semicolons to all lines that need it
    for i in lines:
        new_lines += add_semicolon(i)

    lines = retab(new_lines)

    for i in lines:
        print i

    for k,v in QUOTE_MANAGER.quotes.iteritems():
        print k +": "+colored(repr(v),"red")




