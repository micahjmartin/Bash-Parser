#!/usr/bin/env python3
import sys


class QUOTES:
    """
    Keep a list of all the quotes that are found in the program.
    Give out a unique ID for each quote for later replacement
    """
    def __init__(self):
        self.count = 0
        self.quotes = {}

    def add_quote(self, text, char='"'):
        try:
            # If the quote already exists, get the quote id
            quote_id = list(self.quotes.keys())[
                self.quotes.values().index((char, text))]
        except Exception as E:
            quote_id = "__QUOTE_{}__".format(self.count)
            self.count += 1
            self.quotes[quote_id] = (char, text)
        return quote_id

    def get_quote(self, quote_id):
        quote_char, quote = self.quotes[quote_id]
        # quote = repr(quote)
        quote = quote.replace("\n", "\\n").replace("\t", "\\t")
        return "{0}{1}{0}".format(quote_char, quote)


def find_comment(line):
    # Search for a comment in a line. If there is a comment, separate it out
    line = line.strip()
    # If we are within quotes, what is the quote character
    in_quote = ""
    quote_chars = ("'", '"')  # The characters that we count as a quote

    comment = ""  # The comment line to spit out
    result = ""  # The code that is within the line to spit out

    # Loop through every character in the line
    for i in range(len(line)):
        ch = line[i]  # The character at a given index
        # If we are not in a quote and we find a quote, set the quote character
        if ch in quote_chars and in_quote == "":
            in_quote = ch
        # We are already in a quote, so check if this closes it
        elif ch == in_quote:
            # TODO Do a real escape test.
            if i >= 1 and line[i-1] != "\\":
                in_quote = ""
        if ch == "#" and in_quote == "":
            result = line[:i]  # the line is everything up until the #
            comment = line[i:]  # the comment is everything after the #
            return result.strip(), comment.strip()


def remove_quotes(QUOTE_MANAGER, line):
    # Remove all the quotes in the line and replace them with a unique ID
    line = line.strip()
    quote_start = 0
    # character that we are searching for if we are in a quote
    quote_char = ""
    # The characters that we count as a quote
    quote_chars = ("'", '"')

    output_line = []
    # Loop through every character in the line
    for i in range(len(line)):
        ch = line[i]  # The character at a given index
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
    return "".join(output_line)


def add_semicolon(line):
    """
    Adds a semi colon if the line needs it
    line: (str) line to check
    return: (str) the line
    """
    line = line.strip()
    words = line.split()
    # return nothing if there are no words
    if not words or len(line) == 0:
        return ""
    if line[0] == "#":
        # If its a comment, just skip the rest of the parsing
        return line

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
    return line


def split_lines(line):
    line = line.strip()
    words = line.split()
    # return nothing if there are no words
    if not words or len(line) == 0:
        return ""
    if "{" in line and "()" in line:
        if line.index("()") < line.index("{"):
            line = line.replace("{", "\n{\n")
    # Check for certain words and put them on their own line
    split_words = ("then", "do", "else")
    for w in split_words:
        if w == words[0]:
            line = line.replace(w, w + "\n", 1)
    return line.strip()


def split_comments(line):
    comment = ""
    pos = -1
    if "#" in line:
        pos = line.index("#")
        comment = line[pos:]
        line = line[:pos]
    return line.strip(), comment.strip()


def parse_script(QUOTE_MANAGER, text):
    # Remove all the quotes in the string
    text = remove_quotes(QUOTE_MANAGER, text)
    # Substitute the switch end character so we can parse end lines
    text = text.replace(";;", "__CASE_SPECIAL_CHAR__")
    # Get each command separated on a new line
    text = text.replace(";", ";\n")
    # Replace the special character back into it
    text = text.replace("__CASE_SPECIAL_CHAR__", "\n;;\n")

    # split all the lines
    text = text.split("\n")
    # Strip whitespace from the lines
    text = [l.strip() for l in text]
    # Remove empty lines from the text
    text = [_f for _f in text if _f]

    # Split all the comments
    lines = []
    for i in text:
        # Remove duplicate newlines
        i = " ".join(i.split())
        i, comment = split_comments(i)
        i = add_semicolon(i)
        i = split_lines(i)

        if comment != "":
            lines += [comment]
        if i != "":
            lines += [i]

    # Condense and resplit the lines
    lines = "\n".join(lines)
    # split all the lines
    lines = lines.split("\n")
    # Strip whitespace from the lines
    lines = [l.strip() for l in lines]
    # Remove empty lines from the text
    lines = [_f for _f in lines if _f]
    return lines


def retab_lines(lines):
    # Spaces for tabs
    tab_value = "    "
    tab_level = 0
    result = []
    in_case = False
    tab_inc = ["do", "then", "{", "else"]
    tab_dec = ["fi;", "done;", "};", "else", "esac;", "elif", ";;"]
    for line in lines:
        words = line.split()
        for dec in tab_dec:
            if words[0] == dec:
                tab_level -= 1
                if dec == "esac;":
                    in_case = False
        # Add the tabs to the level
        line = tab_value*tab_level + line
        # Have a special case for "switches"
        if words[-1] == "in":
            in_case = True
            tab_level += 1  # Add an extra for reasons
        if line[-1] == ")" and in_case:
            tab_level += 1
        for inc in tab_inc:
            if words[0] == inc:
                tab_level += 1
        result += [line]

    return result


def parse(text, comments=True, retab=True, oneline=False, strip=False):
    # Handle the args
    if oneline:
        comments = False
        retab = False
    elif retab or comments:
        oneline = False

    # Create a manager for all the quotes
    QUOTE_MANAGER = QUOTES()
    lines = parse_script(QUOTE_MANAGER, text)
    # Strip comments
    new_lines = []
    for line in lines:
        if not comments:
            if line[0] == "#":
                continue
        if "__QUOTE_" in line:
            for k in QUOTE_MANAGER.quotes:
                if k in line:
                    q = QUOTE_MANAGER.get_quote(k)
                    line = line.replace(k, q)
        new_lines += [line]
    lines = new_lines
    # Retab
    if retab:
        lines = retab_lines(lines)

    if oneline:
        return " ".join(lines)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage "+__file__+" <filename>")
        quit()
    # open the file and start processing the lines
    lines_pre = ""
    try:
        with open(sys.argv[1]) as fil:
            lines_pre = fil.read()
    except Exception as E:
        pass

    if lines_pre != "":
        print(parse(lines_pre, oneline=True))


if __name__ == '__main__':
    main()
