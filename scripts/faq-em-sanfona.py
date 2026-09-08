#!/usr/bin/env python3
"""Converte as perguntas (###) das seções de Perguntas frequentes em <AccordionGroup>/<Accordion>.
Idempotente: pula seções que já têm AccordionGroup. Uso: python3 scripts/faq-em-sanfona.py"""
import re, glob, os
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTAS=["visao-geral","primeiros-passos","cerebro","tino","inbox","canais","campanhas","scout","metricas","equipe","atendimento","creditos","integracoes","conta"]
def converte_secao(bloco):
    linhas=bloco.split("\n"); cab=linhas[0]; corpo="\n".join(linhas[1:])
    if "<AccordionGroup" in corpo or "\n### " not in "\n"+corpo: return bloco
    partes=re.split(r"\n(?=### )",("\n"+corpo).lstrip("\n"))
    intro=[]; itens=[]
    for p in partes:
        if p.startswith("### "):
            t,_,resto=p.partition("\n"); titulo=t[4:].strip().replace('"',"'")
            itens.append((titulo,resto.strip()))
        else: intro.append(p.strip())
    out=[cab,""]
    if any(intro): out+=[x for x in intro if x]+[""]
    out.append("<AccordionGroup>")
    for titulo,resto in itens:
        corpo_i="\n".join(("  "+l if l.strip() else "") for l in resto.split("\n"))
        out+=[f'  <Accordion title="{titulo}">',corpo_i,"  </Accordion>"]
    out+=["</AccordionGroup>",""]
    return "\n".join(out)
n=0
for pasta in PASTAS:
    for f in glob.glob(os.path.join(D,pasta,"**","*.mdx"),recursive=True):
        s=open(f,encoding="utf-8").read()
        faq_pagina="perguntas-frequentes" in f
        secoes=re.split(r"\n(?=## )",s); novo=[]
        mudou=False
        for sec in secoes:
            if sec.startswith("## ") and ("## Perguntas frequentes" in sec.split("\n")[0] or faq_pagina) and "### " in sec:
                c=converte_secao(sec); mudou|=(c!=sec); novo.append(c)
            else: novo.append(sec)
        if mudou:
            open(f,"w",encoding="utf-8").write("\n".join(novo)); n+=1
print(f"{n} arquivos convertidos")
