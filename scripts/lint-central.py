#!/usr/bin/env python3
"""Verifica os artigos da central: travessão, vocabulário banido, armadilhas de MDX e links para páginas que não existem.
Uso: python3 scripts/lint-central.py"""
import re, os, sys, glob
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVAS=["visao-geral","primeiros-passos","cerebro","tino","inbox","canais","campanhas","scout","metricas","equipe","atendimento","creditos","integracoes","conta","desenvolvedores"]
# slugs do mapa (do guia) + arquivos existentes
slugs=set()
try:
    import json
    nav=json.load(open(os.path.join(D,"docs.json"),encoding="utf-8"))["navigation"]
    def walk(o):
        if isinstance(o,str): slugs.add("/"+o)
        elif isinstance(o,dict): walk(o.get("pages",[])); [walk(v) for k,v in o.items() if k in("tabs","groups","languages")]
        elif isinstance(o,list): [walk(x) for x in o]
    walk(nav)
except Exception: pass
files=[]
for c in NOVAS:
    files+=glob.glob(os.path.join(D,c,"**","*.mdx"),recursive=True)
existing=set()
for f in files:
    existing.add("/"+os.path.relpath(f,D)[:-4])
BAN=[(r"—","travessão"),(r"\bautomatiza\w*|\bautomação\b","automação"),(r"\bfluxos?\b(?! do processo| do grupo)","fluxo"),(r"\bchatbots?\b|\bbots?\b|\brobôs?\b","bot"),(r"\bgente\b","gente"),(r"^.*\btokens?\b.*(cr[eé]dit|consum|custo|\bIA\b|modelo).*$|^.*(cr[eé]dit|consum|custo|\bIA\b|modelo).*\btokens?\b.*$","tokens como unidade de consumo"),(r"<!--","comentário HTML"),(r"\bclique aqui\b","clique aqui"),(r"\bpotencializ\w*|\brevolucion\w*|\bnova era\b|\bpiloto automático\b|\bnunca tira folga\b","venda")]
probs=0
for f in sorted(files):
    rel=os.path.relpath(f,D); s=open(f,encoding="utf-8").read()
    issues=[]
    fm=re.match(r"^---\n(.*?)\n---\n",s,re.S)
    if not fm: issues.append("sem frontmatter")
    else:
        for k in ("title","description"):
            if not re.search(rf"^{k}:\s*\"",fm.group(1),re.M): issues.append(f"frontmatter sem {k}")
    body=s[fm.end():] if fm else s
    # remove comentários mdx e blocos de código para algumas checagens
    nocom=re.sub(r"\{/\*.*?\*/\}","",body,flags=re.S)
    nocode=re.sub(r"```.*?```","",nocom,flags=re.S); nocode=re.sub(r"`[^`\n]*`","",nocode)
    for pat,name in BAN:
        for m in re.finditer(pat,nocode,re.I|re.M):
            ln=body[:body.find(m.group(0))].count("\n")+1 if m.group(0) in body else "?"
            issues.append(f"{name}: '{m.group(0)}'")
    # chaves soltas fora de JSX/comentários: qualquer { não precedido de < ou = e não iniciando {/*
    for m in re.finditer(r"(?<![=<\w])\{(?!/\*)",nocode):
        ctx=nocode[max(0,m.start()-40):m.start()+40].replace("\n"," ")
        if not re.search(r"<\w[^>]*$",nocode[max(0,m.start()-200):m.start()]): issues.append(f"chave solta: …{ctx}…")
    # '#' de título no corpo
    if re.search(r"^# ",body,re.M): issues.append("título '#' no corpo")
    # links internos
    for m in re.finditer(r"\]\((/[^)#\s]+)(#[^)]*)?\)|href=\"(/[^\"#]+)",body):
        link=(m.group(1) or m.group(3))
        if link.startswith("/images/"): continue
        if link not in slugs and link not in existing: issues.append(f"link fora do mapa: {link}")
    # '<' em texto (fora de tags conhecidas)
    for m in re.finditer(r"<(?!/?(Note|Tip|Info|Warning|Steps|Step|Frame|img|CardGroup|Card|Accordion|AccordionGroup|Tabs|Tab|CodeGroup|iframe|video|br)\b)[A-Za-z0-9]",nocode):
        issues.append(f"'<' suspeito: {nocode[m.start():m.start()+30]!r}")
    words=len(re.sub(r"<[^>]+>","",nocode).split())
    if issues:
        probs+=len(issues); print(f"\n{rel} ({words} palavras)"); [print("  -",i) for i in issues]
print(f"\n{len(files)} arquivos verificados · {probs} apontamentos")
