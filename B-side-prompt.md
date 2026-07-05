# B-Side Sync Prompt — LAOS A↔B
## Versão: 1.0 | 2026-07-05
## Para execução em: Máquina B

---

## Instruções de uso

1. **Preencha os placeholders** `<<PLACEHOLDER>>` com os valores reais (obtidos da máquina A)
2. Execute cada passo em ordem, em PowerShell como **Administrador**
3. Não pule passos. Cada passo tem verificação.
4. Se falhar, pare, leia a mensagem de erro, e pergunte ao usuário antes de continuar

---

## 0. Obter valores de A (preencha antes de executar)

De A, obtenha:

| Placeholder | Como obter | Valor |
|---|---|---|
| `<<A_HOSTNAME>>` | Em A: `$env:COMPUTERNAME` | `LAURENT-CPS` |
| `<<A_TAILSCALE_IP>>` | Em A: `tailscale ip -4` | `100.97.85.82` |
| `<<TAILSCALE_AUTH_KEY>>` | Em A: https://login.tailscale.com/admin/settings/keys → Generate → Reusable, tag:laos-sync | `tskey-auth-...` |
| `<<B_HOSTNAME>>` | Ainda nesta máquina B: `$env:COMPUTERNAME` | |
| `<<WINDOWS_USER>>` | Mesmo user nas duas máquinas: `$env:USERNAME` | `Ryzen` |
| `<<BACKUP_DRIVE>>` | Drive externo para backup (ex: D) | |

---

## Passo 1 — Backup

```powershell
$stamp = Get-Date -Format "yyyyMMdd-HHmm"
$dst = "<<BACKUP_DRIVE>>:\laos-B-pre-sync-$stamp"
New-Item -ItemType Directory -Path $dst -Force
robocopy "E:\" "$dst\" /MIR /R:2 /W:3 /MT:4

# Verificar
Test-Path "$dst\projects\LAOS\AGENTS.md"
```
**Saída esperada:** `True`

---

## Passo 2 — Inventário de referências a E:

```powershell
# Salvar inventário
@"
SCHEDULED TASKS:
$(Get-ScheduledTask | Where-Object { ($_.Actions | ForEach-Object { $_.Execute }) -like 'E:\*' } | Format-Table TaskName, State | Out-String)

SERVICES:
$(Get-CimInstance Win32_Service | Where-Object { $_.PathName -like 'E:\*' } | Select-Object Name, PathName | Format-Table | Out-String)

ENV PATH (User):
$([Environment]::GetEnvironmentVariable('PATH', 'User') -split ';' | Where-Object { $_ -like 'E:\*' })

ENV PATH (Machine):
$([Environment]::GetEnvironmentVariable('PATH', 'Machine') -split ';' | Where-Object { $_ -like 'E:\*' })
"@ | Out-File "E:\pre-change-inventory.txt" -Encoding UTF8
Write-Host "Inventario salvo em E:\pre-change-inventory.txt"
```

---

## Passo 3 — Fechar handles em E:

```powershell
# Fechar File Explorer
Get-Process explorer -ErrorAction SilentlyContinue | Stop-Process -Force

# Fechar opencode se rodando
Get-Process opencode, code -ErrorAction SilentlyContinue | Stop-Process -Force

# Aguardar 5s para liberação
Start-Sleep -Seconds 5
```

> **IMPORTANTE:** Após fechar o explorer, o Windows pode não mostrar a barra de tarefas. Não se preocupe — ela volta automaticamente após o passo 14 (reboot).

---

## Passo 4 — Instalar Tailscale

```powershell
winget install --id Tailscale.Tailscale --accept-source-agreements --accept-package-agreements

# Ativar com auth key de A
& "$env:ProgramFiles\Tailscale\tailscale.exe" up --authkey=<<TAILSCALE_AUTH_KEY>>

# Verificar
$bIP = & "$env:ProgramFiles\Tailscale\tailscale.exe" ip -4
Write-Host "IP de B: $bIP"
& "$env:ProgramFiles\Tailscale\tailscale.exe" ping <<A_HOSTNAME>>

# Salvar IP de B para uso futuro
Set-Content -Path "F:\B-tailscale-ip.txt" -Value $bIP
```
**Saída esperada:** "pong from <<A_TAILSCALE_IP>>"

---

## Passo 5 — Identificar volume de E: e trocar letra para F:

```powershell
# Listar volumes
diskpart /s $(New-Item -Path "$env:TEMP\list_vol.txt" -Force -Value @"
list volume
exit
"@ | Select-Object -ExpandProperty FullPath)
```

> Anote o número do volume de E: (ex.: "Volume 3"). Substitua `<<VOLUME_NÚMERO>>` abaixo.

```powershell
$volNum = <<VOLUME_NUMERO>>  # ex.: 3

# Antes de remover, copiar o inventário para o próprio volume (agora em E:)
Copy-Item "E:\pre-change-inventory.txt" "E:\pre-change-inventory-SALVO.txt" -Force

# Atribuir F: ao volume (E: continua existindo como alias)
diskpart /s $(New-Item -Path "$env:TEMP\assign_f.txt" -Force -Value @"
select volume $volNum
assign letter=F
exit
"@ | Select-Object -ExpandProperty FullPath)

# Verificar que F:\projects\LAOS existe
Test-Path "F:\projects\LAOS\AGENTS.md"
```
**Saída esperada:** `True`

```powershell
# Remover letra E: (F: agora é o único alias)
diskpart /s $(New-Item -Path "$env:TEMP\remove_e.txt" -Force -Value @"
select volume $volNum
remove letter=E
exit
"@ | Select-Object -ExpandProperty FullPath)

# Verificar
Test-Path "E:\"     # False (letra removida)
Test-Path "F:\projects\LAOS\AGENTS.md"  # True
```
**Saída esperada:** `False` na primeira, `True` na segunda.

---

## Passo 6 — Atualizar variáveis de ambiente e PATH

```powershell
# PATH do usuário
$userPath = [Environment]::GetEnvironmentVariable('PATH', 'User') -replace 'E:\\', 'F:\\'
[Environment]::SetEnvironmentVariable('PATH', $userPath, 'User')

# Atualizar PATH da sessão atual
$env:Path = $env:Path -replace 'E:\\', 'F:\\'
```

---

## Passo 7 — Clonar LAOS (versão mais recente do git)

```powershell
# Backup do antigo (se houver)
$oldStamp = Get-Date -Format "yyyyMMdd-HHmmss"
if (Test-Path "F:\projects\LAOS") {
    Move-Item "F:\projects\LAOS" "F:\projects\LAOS-OLD-$oldStamp"
}

# Clonar do GitHub (contém todo o sync infrastructure do commit 2714c47)
cd F:\projects
git clone https://github.com/laurentaf/laos.git LAOS
cd LAOS

# Setup inicial
uv sync
```

**Verificar que os scripts de sync existem:**
```powershell
Test-Path "F:\projects\LAOS\scripts\sync\sync-state.ps1"
Test-Path "F:\projects\LAOS\scripts\sync\merge_duckdb.py"
Test-Path "F:\projects\LAOS\scripts\load_env.py"
```
**Saída esperada:** `True` em todos.

---

## Passo 8 — Configurar .env em B

```powershell
cd F:\projects\LAOS

# Copiar templates
Copy-Item env-local-template.txt .env.local
Copy-Item env-shared-template.txt .env.shared

# Ajustar .env.local para B
@"
# .env.local — MÁQUINA LOCAL (NAO sincronizado)
LATADE_DB_PATH=F:\projects\LAOS\memoria\latade.duckdb
LACOUNCIL_DB_PATH=F:\projects\LAOS\memoria\lacouncil.duckdb
"@ | Out-File .env.local -Encoding UTF8 -Force

# .env.shared será sincronizado de A (passo 10)

# Verificar loader
uv run python scripts/load_env.py
```
**Saída esperada:** Mostra as variáveis de ambiente do LAOS.

---

## Passo 9 — Instalar hooks git

```powershell
cd F:\projects\LAOS
.\scripts\setup-hooks.ps1
```
**Saída esperada:** "SUCCESS: hooks installed (pre-commit, post-merge)"

---

## Passo 10 — Configurar SMB share em B (para A puxar de B)

```powershell
# Garantir que memoria/audit existe
New-Item -ItemType Directory -Path "F:\projects\LAOS\memoria\audit" -Force | Out-Null

# Criar share
New-SmbShare -Name "LAOS_STATE" `
    -Path "F:\projects\LAOS\memoria" `
    -FullAccess "$env:USERNAME" `
    -Description "LAOS state sync"

# Habilitar criptografia SMB
Set-SmbShare -Name "LAOS_STATE" -EncryptData $true

# Verificar
Get-SmbShare -Name "LAOS_STATE"
```

---

## Passo 11 — Conectar a A via SMB

```powershell
# Em B: mapear Y: para A
net use Y: \\<<A_TAILSCALE_IP>>\LAOS_STATE /persistent:yes

# Verificar
Test-Path "Y:\lacouncil.duckdb"
```
**Saída esperada:** `True` (se A já tiver rodado o setup-smb-share.ps1)

> Se falhar:
> 1. Em A: rode `tailscale status` — confirme que B aparece como online
> 2. Em A: rode `.\scripts\sync\setup-smb-share.ps1` (admin)
> 3. Tente net use novamente

---

## Passo 12 — Primeira sincronização (pull de A)

```powershell
cd F:\projects\LAOS
.\scripts\sync\sync-state.ps1 -RemoteDrive Y -Direction pull
```
**Saída esperada:** "Pull completo. N propostas merged. 0 conflitos. Push concluido."

---

## Passo 13 — Agendar sync automático

```powershell
cd F:\projects\LAOS
.\scripts\sync\install-sync-task.ps1 -RemoteDrive Y -Direction pull -TaskName "LAOS-Sync-State-B"

# Verificar
Get-ScheduledTask -TaskName "LAOS-Sync-State-B" | Select-Object State, TaskName
```
**Saída esperada:** State=Ready

---

## Passo 14 — Validação final

```powershell
cd F:\projects\LAOS

# 1. Preflight
uv run python scripts/preflight_check.py projects/previsao-concursos
if ($LASTEXITCODE -ne 0) { Write-Warning "Preflight falhou" }

# 2. Listar capabilities
uv run python scripts/list_capabilities.py

# 3. Verificar state sincronizado
uv run python -c "
import duckdb
c = duckdb.connect('F:/projects/LAOS/memoria/lacouncil.duckdb', read_only=True)
print('propostas:', c.execute('SELECT COUNT(*) FROM propostas').fetchone()[0])
print('votos:', c.execute('SELECT COUNT(*) FROM votos').fetchone()[0])
"

# 4. Tailscale status
& "$env:ProgramFiles\Tailscale\tailscale.exe" status

Write-Host ""
Write-Host "========================================"
Write-Host "  SYNCHRONIZED — B is ready" -ForegroundColor Green
Write-Host "  Path: F:\projects\LAOS"
Write-Host "  Sync: every 15 min"
Write-Host "========================================"
```

---

## Passo 15 — Reboot

```powershell
Restart-Computer -Force
```

Após o reboot, faça login e confirme:
```powershell
Test-Path "F:\projects\LAOS\AGENTS.md"  # True
Test-Path "E:\"                          # False (letra removida)
Get-ScheduledTask -TaskName "LAOS-Sync-State-B"  # Ready
```

---

## Rollback (se algo quebrar)

### Se o renome E:→F: falhou:
```powershell
# O backup está em <<BACKUP_DRIVE>>:\laos-B-pre-sync-*
robocopy "<<BACKUP_DRIVE>>:\laos-B-pre-sync-<<STAMP>>\projects\LAOS" "E:\projects\LAOS" /MIR
```

### Se o Tailscale falhou:
```powershell
tailscale logout
```

### Se o clone falhou:
```powershell
Remove-Item "F:\projects\LAOS" -Recurse -Force
Move-Item "F:\projects\LAOS-OLD-*" "F:\projects\LAOS"
```

---

## Apêndice: O que foi criado na Parte 1 (em A)

Commit `2714c47` na branch `main` do repositório `github.com/laurentaf/laos`:

| Arquivo | Função |
|---|---|
| `scripts/sync/sync-state.ps1` | Orquestrador de sync (lock → pull → merge → push → audit) |
| `scripts/sync/merge_duckdb.py` | Merge de 2 DuckDBs LACOUNCIL com dedup UUID + remap SEQUENCE |
| `scripts/sync/install-sync-task.ps1` | Registra tarefa agendada Windows (15min) |
| `scripts/hooks/post-merge.ps1` | Git hook — auto uv sync após cada git pull |
| `scripts/load_env.py` | Loader de .env.local + .env.shared |
| `scripts/setup-tailscale.ps1` | Instala Tailscale e captura credenciais |
| `env-shared-template.txt` | Template de .env.shared (chaves de API) |
| `env-local-template.txt` | Template de .env.local (paths absolutos) |
| `setup.ps1` | Atualizado para criar .env.shared + .env.local |
| `scripts/setup-hooks.ps1` | Corrigido REPO_ROOT + adiciona post-merge hook |
| `.gitignore` | Adicionado .env.shared |
| `pyproject.toml` | Adicionado python-dotenv |
