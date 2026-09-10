#!/usr/bin/env python3
"""Troca as grades <CardGroup>/<Card> de artigos relacionados pela lista em linhas
(<Lista>/<Artigo>, em components/lista-artigos.jsx), no padrão de central de ajuda.
As homes (index.mdx nos três idiomas) ficam em grade, como a home da Intercom.
Idempotente. Uso: python3 scripts/lista-de-artigos.py"""
import glob, os, re
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPORT='import { Lista, Artigo } from "/components/lista-artigos.jsx";'
ATTR=re.compile(r'(\w+)="([^"]*)"')
CARD=re.compile(r'<Card\b([^>]*)>(.*?)</Card>',re.S)
GRUPO=re.compile(r'<CardGroup\b[^>]*>(.*?)</CardGroup>',re.S)

def card(m):
    a=dict(ATTR.findall(m.group(1))); texto=" ".join(m.group(2).split())
    t=a.get("title",""); h=a.get("href","")
    return f'  <Artigo titulo="{t}" href="{h}">{texto}</Artigo>' if texto else f'  <Artigo titulo="{t}" href="{h}" />'

def grupo(m):
    itens=[card(c) for c in CARD.finditer(m.group(1))]
    return "<Lista>\n"+"\n".join(itens)+"\n</Lista>"

n=0
for f in glob.glob(os.path.join(D,"**","*.mdx"),recursive=True):
    rel=os.path.relpath(f,D)
    if rel in ("index.mdx","en/index.mdx","es/index.mdx") or rel.startswith(("inventario/","node_modules/")): continue
    s=open(f,encoding="utf-8").read()
    if "<CardGroup" not in s: continue
    novo=GRUPO.sub(grupo,s)
    fm=re.match(r"^---\n.*?\n---\n",novo,re.S)
    if IMPORT not in novo and fm:
        novo=novo[:fm.end()]+"\n"+IMPORT+"\n"+novo[fm.end():]
    if novo!=s: open(f,"w",encoding="utf-8").write(novo); n+=1
print(n,"arquivos convertidos para lista")
