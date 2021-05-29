from onedef.parser import Parser
from onedef.transpiler.server import ServerCompiler
from onedef.transpiler.client import ClientTranspiler

with open ("../../example_simple.onedef", "r") as example_file:
    example_lines = example_file.readlines ()
example_lines = list (map (lambda line: line.replace ("\n", ""), example_lines))

parsed = Parser.parse (example_lines)
print (parsed)
# server = ServerCompiler.compile (parsed)
# client = ClientCompiler.compile (parsed)
# server.run_with (client)
