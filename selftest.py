import importlib
m = importlib.import_module("md2html")
assert hasattr(m, "main") and callable(m.main), "main() missing in md2html"
print("selftest OK: md2html importable, main() callable")
