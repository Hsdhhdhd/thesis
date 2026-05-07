import re, glob

PAT = re.compile(r'\\cite[pt]?\{([^}]+)\}')

def collect_keys(folder):
    keys = set()
    for f in glob.glob(folder + '/chapters/*.tex'):
        with open(f, 'r', encoding='utf-8') as fp:
            text = fp.read()
        for m in PAT.finditer(text):
            for k in m.group(1).split(','):
                keys.add(k.strip())
    return keys

fet = collect_keys(r"d:/最终论文/KU-Leuven-master-thesis-template-FET-main/KU-Leuven-master-thesis-template-FET-main")
ea  = collect_keys(r"d:/最终论文/4.30新论文模板/fiiw_thesis_ea_template(1)")
print("FET citation keys:", len(fet))
print("EA  citation keys:", len(ea))
print()
print("Missing in EA:")
for k in sorted(fet - ea):
    print(" ", k)
print()
print("New in EA (extra/unexpected):")
for k in sorted(ea - fet):
    print(" ", k)
