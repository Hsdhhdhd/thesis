import os, re
os.chdir(r"d:/最终论文/4.30新论文模板/fiiw_thesis_ea_template(1)/chapters")
section_re = re.compile(r"^\s*\\(sub)?section\*?\{")
for f in sorted(os.listdir('.')):
    if not f.endswith('.tex'): continue
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    issues = []
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '' and lines[i-1].strip() == '':
            issues.append((i+1, 'consecutive blank'))
        if i > 0 and line.strip() == '' and section_re.match(lines[i-1]):
            issues.append((i+1, 'blank after section header'))
    print(f, ':', len(issues), 'issues')
    for ln, kind in issues[:10]:
        print(f'  line {ln}: {kind}')
