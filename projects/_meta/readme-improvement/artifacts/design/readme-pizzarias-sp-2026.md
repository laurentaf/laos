<!--
  Top 100 Pizzarias de São Paulo 2026 — Power BI report
  README.md  |  github.com/laurentaf/pizzarias-sp-2026
  Brand: Data-driven food mapping, São Paulo pizza scene
  Tone: Friendly, practical, bilingual (EN + PT).
  Adapted from the LAOS README (20/20) inline-HTML pattern.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Emblem: pizza slice + map pin -->
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#E17055" stroke-width="1.5" fill="none" opacity="0.3"/>
  <!-- Pizza slice -->
  <path d="M32 16 L16 48 L48 48 Z" stroke="#E17055" stroke-width="2" fill="none" stroke-linejoin="round" opacity="0.4"/>
  <line x1="32" y1="16" x2="28" y2="36" stroke="#E17055" stroke-width="1.5" opacity="0.5"/>
  <line x1="32" y1="16" x2="38" y2="32" stroke="#E17055" stroke-width="1.5" opacity="0.5"/>
  <line x1="32" y1="16" x2="22" y2="40" stroke="#E17055" stroke-width="1.5" opacity="0.5"/>
  <!-- Map pin -->
  <path d="M48 32 Q48 42 42 48 Q38 52 36 54 Q34 56 32 56 Q30 56 28 54 Q26 52 22 48 Q16 42 16 32 Q16 22 24 16 Q28 12 32 12 Q36 12 40 16 Q48 22 48 32 Z" stroke="#D63031" stroke-width="2" fill="none" opacity="0.5"/>
  <circle cx="32" cy="32" r="6" stroke="#D63031" stroke-width="2" fill="none" opacity="0.6"/>
  <circle cx="32" cy="32" r="2" fill="#E17055" opacity="0.7"/>
</svg>

<br/>

# 🍕 Top 100 Pizzarias de São Paulo 2026

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Power%20BI-Report-F2C811?style=flat&logo=powerbi&logoColor=000" alt="Power BI Report"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=fff" alt="Python 3.11"/>
  &nbsp;
  <img src="https://img.shields.io/badge/n8n-Automation-EA4C88?style=flat&logo=n8n&logoColor=fff" alt="n8n Automation"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-COMPLETE-00b894?style=flat" alt="Status: COMPLETE"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #E17055;opacity:0.3;"/>

</div>

> **EN:** Interactive Power BI report of the 100 best pizzerias in São Paulo, mapped by geographic zone — with automated logo scraping via n8n.
>
> **PT:** Relatório interativo em Power BI com as 100 melhores pizzarias de São Paulo, distribuídas por zona geográfica — com scraping automatizado de logos via n8n.

---

## 📋 Project Files / Arquivos do Projeto

<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid #E17055;border-bottom-opacity:0.2;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">File / Arquivo</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Description / Descrição</th>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>100PizzariasSP.pbix</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Interactive Power BI report / Relatório Power BI interativo</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>data/enderecos.csv</code></td>
    <td style="padding:8px 14px;opacity:0.7;">100 pizzerias with address, neighborhood, zone, coordinates</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>data/depara_zonas_sp.csv</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Subprefecture → Zone mapping / Mapeamento Subprefeitura → Zona</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>data/subprefeituras-sp.json</code></td>
    <td style="padding:8px 14px;opacity:0.7;">GeoJSON of São Paulo subprefectures</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>data/sp_zonas_topo_final.json</code></td>
    <td style="padding:8px 14px;opacity:0.7;">GeoJSON of SP geographic zones</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>n8n/workflow-scrape-logos.json</code></td>
    <td style="padding:8px 14px;opacity:0.7;">n8n workflow for automated logo scraping</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>scripts/scrape_logos.py</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Alternative Python script for logo scraping</td>
  </tr>
</table>

---

## 🗺️ Dataset Structure / Estrutura dos Dados

`data/enderecos.csv` columns:

<table style="font-size:0.85em;border-collapse:separate;border-spacing:0;">
  <tr><td style="padding:6px 12px;font-weight:500;">Posição</td><td style="padding:6px 12px;opacity:0.6;">Ranking position (1–100)</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Pizzaria</td><td style="padding:6px 12px;opacity:0.6;">Pizzeria name</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Endereço</td><td style="padding:6px 12px;opacity:0.6;">Street address</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Bairro</td><td style="padding:6px 12px;opacity:0.6;">Neighborhood</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Cidade / Estado / CEP</td><td style="padding:6px 12px;opacity:0.6;">City, State, ZIP</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Zona</td><td style="padding:6px 12px;opacity:0.6;">Geographic zone (Norte, Sul, Leste, Oeste, Centro)</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Latitude / Longitude</td><td style="padding:6px 12px;opacity:0.6;">Geographic coordinates</td></tr>
</table>

---

## 🤖 Automated Logo Scraping / Captura Automatizada de Logos

### The Challenge / O Desafio

The Power BI report needs pizzeria logos to enrich the visual experience. Manually collecting 85 logos (positions 16–100) would be extremely time-consuming.

O Power BI precisa dos logos das pizzarias para enriquecer o relatório. Buscar 85 logos manualmente (posições 16–100) seria muito demorado.

### Solution 1: n8n Workflow (no API keys)

<div align="center" style="margin:20px 0;">

```
┌──────────────────────┐
│  Read enderecos.csv  │
│  (posições 16–100)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Google Search:      │
│  "{nome} pizzaria    │
│   logo"              │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Parse HTML →        │
│  extrai URL da imagem│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Download →          │
│  logos/{posicao}-    │
│  {nome}.jpg          │
└──────────────────────┘
```

</div>

1. **Read File** — loads pizzarias 16–100 from CSV
2. **HTTP Request** — searches Google for `"Nome da Pizzaria pizzaria logo"`
3. **Code Node** — extracts image URLs from the HTML
4. **HTTP Request** — downloads the image
5. **Write Binary File** — saves as `{posicao}-{nome}.jpg`

#### Setup

```bash
# Start n8n via Docker
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n

# Access: http://localhost:5678
# Import: n8n/workflow-scrape-logos.json
# Activate and run — no API keys needed
```

### Solution 2: Python Script (no API keys)

```bash
cd scripts
pip install requests beautifulsoup4
python scrape_logos.py --start 16 --end 100
```

The script searches Google Images and downloads each pizzeria's logo automatically.

#### Output Location / Onde são salvos

Logos are saved to `logos/` in the project root (excluded from git via `.gitignore`).

---

## 🚀 How to Use / Como Usar

```bash
# Clone the repo
git clone https://github.com/laurentaf/pizzarias-sp-2026.git
cd pizzarias-sp-2026

# For the Power BI report: open 100PizzariasSP.pbix
# For automated logo scraping:
#   Option 1: n8n (see above)
#   Option 2: Python script (see above)
```

---

## Contributing / Contribuindo

<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.85em;">
  <tr style="border-bottom:1px solid #E17055;border-bottom-opacity:0.2;">
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">EN</th>
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">PT</th>
  </tr>
  <tr>
    <td style="padding:8px 12px;opacity:0.7;">Found a missing pizzeria? Have a better logo? Open an issue or submit a PR. Data corrections and new data sources are always welcome.</td>
    <td style="padding:8px 12px;opacity:0.7;">Encontrou uma pizzaria faltando? Tem um logo melhor? Abra uma issue ou envie um PR. Correções de dados e novas fontes são sempre bem-vindas.</td>
  </tr>
</table>

---

## Licença / License

<div style="margin:16px 0;">

**ISC** — see [`LICENSE`](https://github.com/laurentaf/pizzarias-sp-2026/blob/main/LICENSE) for the full text / veja o arquivo [`LICENSE`](https://github.com/laurentaf/pizzarias-sp-2026/blob/main/LICENSE) para o texto completo.

Dados coletados de fontes públicas / Data collected from public sources. Projeto pessoal / Personal project.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.25;font-size:0.8em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#E17055" stroke-width="1.5" fill="none" opacity="0.15"/>
  <path d="M32 16 L16 48 L48 48 Z" stroke="#E17055" stroke-width="2" fill="none" stroke-linejoin="round" opacity="0.4"/>
  <path d="M48 32 Q48 42 42 48 Q38 52 36 54 Q34 56 32 56 Q30 56 28 54 Q26 52 22 48 Q16 42 16 32 Q16 22 24 16 Q28 12 32 12 Q36 12 40 16 Q48 22 48 32 Z" stroke="#D63031" stroke-width="2" fill="none" opacity="0.4"/>
</svg>
<br/>
🍕 Top 100 Pizzarias de São Paulo 2026
</div>
