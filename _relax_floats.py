import os, re
os.chdir(r"d:/最终论文/4.30新论文模板/fiiw_thesis_ea_template(1)/chapters")
for f in ['02-design.tex', '03-implementation.tex', '04-evaluation.tex']:
    with open(f, 'r', encoding='utf-8') as fp:
        text = fp.read()
    new_text = re.sub(r'\\begin\{figure\*\}\[t\]', r'\\begin{figure*}[!tbp]', text)
    if new_text != text:
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(new_text)
        print(f, 'updated')
    else:
        print(f, 'no change')
