import browser
import sys
import tb as traceback

_launchtext = """CS61A Python Web Interpreter
--------------------------------------------------------------------------------
Welcome to the 61A Python web interpreter! 
Check out the code for this app on GitHub.

To visualize a list, call draw(<list>).
To draw list visualizations automatically, call autodraw().
To view an environment diagram of your entire program, call visualize().
To launch an editor associated with your console, call editor().
"""

_credits = """    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands
    for supporting Python development.  See www.python.org for more information."""

_copyright = """Copyright (c) 2012, Pierre Quentel pierre.quentel@gmail.com
All Rights Reserved.

Copyright (c) 2001-2013 Python Software Foundation.
All Rights Reserved.

Copyright (c) 2000 BeOpen.com.
All Rights Reserved.

Copyright (c) 1995-2001 Corporation for National Research Initiatives.
All Rights Reserved.

Copyright (c) 1991-1995 Stichting Mathematisch Centrum, Amsterdam.
All Rights Reserved."""

_license = """Copyright (c) 2012, Pierre Quentel pierre.quentel@gmail.com
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer. Redistributions in binary
form must reproduce the above copyright notice, this list of conditions and
the following disclaimer in the documentation and/or other materials provided
with the distribution.
Neither the name of the <ORGANIZATION> nor the names of its contributors may
be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


class Stream:
    def __init__(self, obj):
        self.obj = obj

    def write(self, raw):
        self.obj.write(raw)


stdout = Stream(browser.self.stdout)
stderr = Stream(browser.self.stderr)


def credits():
    print(_credits)


credits.__repr__ = lambda: _credits


def copyright():
    print(_copyright)


copyright.__repr__ = lambda: _copyright


def license():
    print(_license)


license.__repr__ = lambda: _license


class Trace:
    def __init__(self):
        self.buf = ""

    def write(self, data):
        self.buf += str(data)

    def format(self):
        """Remove calls to function in this script from the traceback."""
        lines = self.buf.split("\n")
        stripped = [lines[0]]
        for i in range(1, len(lines), 2):
            if __file__ in lines[i]:
                continue
            stripped += lines[i : i + 2]
        return "\n".join(stripped)


def print_tb():
    trace = Trace()
    traceback.print_exc(file=trace)
    err(trace.format())


def syntax_error(args):
    info, filename, lineno, offset, line = args
    print(f"  File {filename}, line {lineno}")
    print("    " + line)
    print("    " + offset * " " + "^")
    print("SyntaxError:", info)
    flush()


OUT_BUFFER = ""
src = ""


def write(data):
    global OUT_BUFFER
    OUT_BUFFER += str(data)
    flush()


def flush():
    global OUT_BUFFER, src
    stdout.write(OUT_BUFFER)
    src += OUT_BUFFER
    OUT_BUFFER = ""


def err(data):
    global src
    src += data
    stderr.write(data)


sys.stdout.write = write
sys.stderr.write = err
sys.stdout.__len__ = sys.stderr.__len__ = lambda: len(OUT_BUFFER)

history = []
current = 0
_status = "main"  # or "block" if typing inside a block

autodraw_active = False


def json_repr(elem):
    if isinstance(elem, list):
        elem_reprs = [json_repr(x) for x in elem]
        return "[" + ", ".join(elem_reprs) + "]"
    elif isinstance(elem, str):
        return '"' + repr(elem)[1:-1] + '"'
    elif isinstance(elem, dict):
        key_val_reprs = [
            json_repr(key) + ": " + json_repr(val) for key, val in elem.items()
        ]
        return "{" + ", ".join(key_val_reprs) + "}"
    elif isinstance(elem, bool):
        if elem:
            return "true"
        else:
            return "false"
    elif isinstance(elem, int):
        return '"' + repr(elem) + '"'
    else:
        raise Exception("Unable to serialize object of type " + str(old_type(elem)))


def wrap_debug(out):
    print("DRAW: " + json_repr(out))


def autodraw():
    global autodraw_active
    autodraw_active = True
    print("Call disable_autodraw() to disable automatic visualization of lists.")


def disable_autodraw():
    global autodraw_active
    autodraw_active = False
    print("Autodraw disabled.")


def atomic(elem):
    listlike = list, tuple
    return not isinstance(elem, listlike) and not is_tree(elem)


def is_tree(elem):
    return old_type(elem).__name__ == "Tree" or hasattr(elem, "__is_debug_tree")


def inline(elem):
    inline = int, bool, float, str, old_type(None)
    return isinstance(elem, inline)


def is_leaf(tree):
    return (
        isinstance(tree, list)
        and len(tree) == 1
        or hasattr(tree, "branches")
        and not tree.branches
    )


def label(tree):
    return tree[0] if isinstance(tree, list) else tree.label


def branches(tree):
    return tree[1:] if isinstance(tree, list) else tree.branches


def draw(lst):
    heap = {}

    def draw_worker(elem):
        if inline(elem):
            return ["inline", repr(elem)]
        if not id(elem) in heap:
            heap[id(elem)] = None
            if atomic(elem):
                val = ["atomic", ["inline", repr(elem)]]
            elif len(elem) == 0:
                val = ["atomic", ["inline", "Empty list"]]
            else:
                val = ["list", [draw_worker(x) for x in elem]]
            heap[id(elem)] = val
        return ["ref", id(elem)]

    def draw_tree(tree):
        if is_leaf(tree):
            return [repr(label(tree))]
        return [repr(label(tree)), [draw_tree(branch) for branch in branches(tree)]]

    if is_tree(lst):
        data = ["Tree", draw_tree(lst)]
    else:
        data = [draw_worker(lst), heap]

    wrap_debug(data)


def visualize():
    print("DEBUG: ")


def editor():
    print("EDITOR: ")


def record_exec(code, wrap):
    if wrap:
        out = "try:\n"
        for line in code.split("\n"):
            out += "\t" + line + "\n"
        out += "except Exception as e:\n\tprint(e)\n"
        record_exec(out, False)
    else:
        print("EXEC: " + code)


def input(prompt=""):
    print(prompt, end="")
    return browser.self.blockingInput.wait(
        "input() is not supported in your browser. Try using Chrome instead!"
    )


class TreeList(list):
    pass


old_type = type


def type(arg):
    if isinstance(arg, TreeList):
        return list
    return old_type(arg)


def replace_trees(namespace):
    if "tree" in namespace:
        func = namespace["tree"]

        try:
            if hasattr(func(1), "__is_debug_tree"):
                return
        except:
            return

        def tree_debug(*args, **kwargs):
            out = TreeList(func(*args, **kwargs))
            out.__is_debug_tree = True
            return out

        namespace["tree"] = tree_debug


old_open = open


def open(file, *args, **kwargs):
    file = "/api/load_file/" + file
    return old_open(file, *args, **kwargs)


class LocalFinder:
    @staticmethod
    def find_spec(name, path, target_module=None):
        if path is not None or target_module is not None:
            return None

        try:
            contents = browser.self.filesystem.read("/cs61a/proj04/" + name + ".py")
        except:
            return

        class Loader:
            origin = "cs61a/hw01/hw01.py"
            has_location = True
            submodule_search_locations = None
            loader_state = None
            cached = None
            parent = None

            @staticmethod
            def create_module(spec):
                return None

            @staticmethod
            def exec_module(module):
                exec(contents, module.__dict__)

        loader = Loader()
        loader.name = name
        loader.loader = loader
        return loader


sys.meta_path = [LocalFinder()] + sys.meta_path


editor_ns = {
    "credits": credits,
    "copyright": copyright,
    "license": license,
    "autodraw": autodraw,
    "disable_autodraw": disable_autodraw,
    "draw": draw,
    "visualize": visualize,
    "editor": editor,
    "input": input,
    "open": open,
    "__name__": "__main__",
    "type": type,
}

firstLine = True


def handleInput(line):
    global src, _status, firstLine

    if firstLine:
        if line.strip():
            try:
                exec(line, editor_ns)
                replace_trees(editor_ns)
                record_exec(line, False)
            except Exception as e:
                if not isinstance(e, SyntaxError):
                    record_exec(line, True)
                print_tb()
            err(">>> ")
        else:
            write(_launchtext)
            err("\n>>> ")
            # doc['code'].value += 'Type "copyright", "credits" or "license" for more information.'
        firstLine = False
        return

    src += line[:-1]

    if _status == "main":
        current_line = src[src.rfind(">>>") + 4 :]
        src = ">>> " + current_line
    elif _status == "3string":
        current_line = src[src.rfind(">>>") + 4 :]
        src = ">>> " + current_line
        current_line = current_line.replace("\n... ", "\n")
    else:
        current_line = src[src.rfind("...") + 4 :]

    src += "\n"

    if _status == "main" and not current_line.strip():
        err(">>> ")
        return

    if _status == "main" or _status == "3string":
        try:
            _ = editor_ns["_"] = eval(current_line, editor_ns)
            replace_trees(editor_ns)
            record_exec(current_line, False)
            flush()
            if _ is not None:
                write(repr(_) + "\n")
                if not atomic(_) and autodraw_active:
                    draw(_)
            flush()
            err(">>> ")
            _status = "main"
        except IndentationError:
            err("... ")
            _status = "block"
        except SyntaxError as msg:
            if str(msg) == "invalid syntax : triple string end not found" or str(
                msg
            ).startswith("Unbalanced bracket"):
                err("... ")
                _status = "3string"
            elif str(msg) == "eval() argument must be an expression":
                try:
                    exec(current_line, editor_ns)
                    replace_trees(editor_ns)
                    record_exec(current_line, False)
                except Exception as e:
                    print_tb()
                    if not isinstance(e, SyntaxError):
                        record_exec(current_line, True)
                flush()
                err(">>> ")
                _status = "main"
            elif str(msg) == "decorator expects function":
                err("... ")
                _status = "block"
            else:
                syntax_error(msg.args)
                err(">>> ")
                _status = "main"
        except Exception as e:
            # the full traceback includes the call to eval(); to
            # remove it, it is stored in a buffer and the 2nd and 3rd
            # lines are removed
            if not isinstance(e, SyntaxError):
                record_exec(current_line, True)
            print_tb()
            err(">>> ")
            _status = "main"
    elif current_line == "":  # end of block
        block = src[src.rfind(">>>") + 4 :]
        src = ">>> " + block
        block = block.splitlines()
        block = [block[0]] + [b[4:] for b in block[1:]]
        block_src = "\n".join(block)
        # status must be set before executing code in globals()
        _status = "main"
        try:
            _ = exec(block_src, editor_ns)
            replace_trees(editor_ns)
            record_exec(block_src, False)
            if _ is not None:
                print(repr(_))
        except Exception as e:
            if not isinstance(e, SyntaxError):
                record_exec(block_src, True)
            print_tb()
        flush()
        err(">>> ")
    else:
        err("... ")


browser.self.stdin.on(handleInput)
