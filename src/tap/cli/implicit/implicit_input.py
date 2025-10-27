import sys


class ImplicitInput:
    """
    A class that handles implicit input from standard input (stdin).
    Tap's design is intended to be monadic, where you can concatenate input with multiple runs of the cli in a pipe,
    and context is wrapped in XML context tags.
    """

    def __init__(self):
        # Detect and read from stdin
        if sys.stdin.isatty():
            self.input_data = ""
            self.is_piped = False
        else:
            self.input_data = sys.stdin.read()
            self.is_piped = True

    def wrap_input(self, context_tag="context"):
        """
        Wrap the input data in XML context tags if input data exists.
        :param context_tag: The XML tag to use for wrapping the context.
        :return: The wrapped input data or an empty string.
        """
        if self.is_piped:
            return f"<{context_tag}>\n{self.input_data}\n</{context_tag}>\n"
        return ""
