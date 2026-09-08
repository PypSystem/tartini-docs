#!/usr/bin/env python3
"""Garante uma linha horizontal (---) antes de cada seção ## dos artigos, como na central da Intercom.
Idempotente. Uso: python3 scripts/separadores.py"""
import glob, os, re
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTAS=["visao-geral","primeiros-passos","cerebro","tino","inbox","canais","campanhas","scout","metricas","equipe","atendimento","creditos","integracoes","conta","desenvolvedores","en","es"]
n=0
for pasta in PASTAS:
    for f in glob.glob(os.path.join(D,pasta,"**","*.mdx"),recursive=True):
        s=open(f,encoding="utf-8").read()
        fm=re.match(r"^---\n.*?\n---\n",s,re.S)
        head,body=(s[:fm.end()],s[fm.end():]) if fm else ("",s)
        linhas=body.split("\n"); out=[]; fence=False
        for i,l in enumerate(linhas):
            if l.startswith("```"): fence=not fence
            if not fence and l.startswith("## "):
                # remove linhas em branco e --- imediatamente anteriores, depois insere separador padronizado
                while out and out[-1].strip() in ("","---"): out.pop()
                if out: out+=["","---",""]
            out.append(l)
        novo=head+"\n".join(out)
        if novo!=s: open(f,"w",encoding="utf-8").write(novo); n+=1
print(f"{n} arquivos com separadores ajustados")
