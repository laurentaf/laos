# Convenções de dados

Convensões transversais para tratamento de dados em LAOS.
Conhecimento transversal — não específico de uma capability.
Capacities de domínio podem ter convenções próprias; este arquivo só
lista o que vale para múltiplos domínios.

## _commomdata — diretório compartilhado cross-project

**Path:** `E:\projects\_commomdata\`

**Propósito:** Hospedar **fontes de grounding** (livros, papers, datasets
públicos) reutilizáveis em múltiplos projetos. Não é dado de projeto
único — é **referência**.

**Quem coloca:** Usuário, manualmente. Sem upload automático.

**Quem consome:** Qualquer projeto LAOS pode referenciar arquivos em
`_commomdata/` por path absoluto.

**Versionamento:** Não versionado (fora de qualquer repositório git).
Conteúdo estável (livros, papers, datasets de referência). Mudanças
devem ser coordenadas com o usuário.

**Convenção de nome:** `<YYYYMMDDHHMMSS>_<title>.<ext>` (timestamp +
título). Exemplo real:

```
E:\_commomdata\10_20230923061708_Basic-econometrics-5th-ed-gujarati-and-porter_pdf.pdf
```

O prefixo numérico é o timestamp no formato `YYYYMMDDHHMMSS` no qual o
arquivo foi colocado no diretório. Isso facilita ordenação e auditoria
sem precisar inspecionar metadata do filesystem.

**Capabilities que referenciam:** Todas podem ler. LAECON inclui
`common_data_root` configurável que aponta para este path por padrão
em seus projetos derivados.

**Projetos de exemplo:**
- `projects/_meta/laecon-capability/` — usa Gujarati PDF como base
  teórica para a capability de econometria (LAECON).
- Quirk's article sobre NPS driver analysis — referenciado como URL,
  não baixado para `_commomdata/` (a URL é estável e indexável por
  ferramentas como `exa`/`context7`).

**Quando NÃO usar `_commomdata`:**
- Dados de projeto (tabelas, snapshots, artefatos) → vão para o
  child repo do projeto, em `artifacts/data/` ou similar.
- Outputs de execução (logs, métricas, predições) → vão para o child
  repo do projeto, nunca em `_commomdata/`.
- Dados que mudam com frequência → fora; `_commomdata` é para fontes
  estáveis de referência.

---

## Como adicionar uma nova convenção aqui

Antes de adicionar: a convenção é mesmo transversal a múltiplos
domínios? Se só vive em dados, vai para `../latade/`. Se só vive em
design, vai para `../ladesign/docs/`. Se só vive em automação, vai
para `../lan8n/`. Este arquivo é a exceção, não a regra.

Critério prático: se 2+ capabilities declaram a mesma convenção nos
respectivos KB/docs, vale a pena promover para cá.
