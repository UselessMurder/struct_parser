#!/usr/bin/python2
import re, os, sys
from pycparser import c_parser, c_ast, parse_file

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: parser.py PATH")
        raise SystemExit

    if not os.path.exists(sys.argv[1]):
        print("File %s not exists!" % sys.argv[1])
        raise SystemExit

    try:
        rname = re.compile('\/\/ (.*)\n')
        ast = parse_file(sys.argv[1], use_cpp=True)
        structs = ast.ext[0].init.exprs

        f = open(sys.argv[1])
        lines = f.readlines()
        f.close()

        apis = dict()

        for struct in structs:
            name   = struct.exprs[5].exprs[0].exprs[2].exprs[0].value
            params = struct.exprs[5].exprs[0].exprs[2].exprs[10].exprs
            apis[name] = dict()
            for param in params:
                param_name = rname.search(lines[param.coord.line - 2]).group(1)
                key = 'call' 
                if param.exprs[1].name == 'true':
                    key = 'ret'
                if key not in apis[name]:
                    apis[name][key] = []
                apis[name][key].append((param_name, param.exprs[2].name))

        f = open(sys.argv[1] + ".py", "w+")
        f.write("api_table = {\n")
        for api, types in apis.iteritems():
            f.write("   '%s': {\n" % api.split("!")[1][:-1])
            for f_type, params  in types.iteritems():
                f.write("       '%s': [\n" % f_type)
                for param in params:
                    f.write("           ('%s', %s),\n" % (param[0], param[1]))
                f.write("       ],\n")
            f.write("   },\n")
        f.write("}\n")
        f.close()
    except Exception as e:
        print("Something was wrong: " + e)
        raise SystemExit
