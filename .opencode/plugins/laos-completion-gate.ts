/**
 * LAOS Completion Gate — Enforcement de completude pós-resposta
 *
 * Provenance:
 *   - LACOUNCIL discussão Jun 2026: agents param no meio, sem hook pós-resposta
 *   - Descoberta: OpenCode Desktop v1.17.9 TEM `experimental.text.complete`
 *     (processor.ts L505-514) — hook que dispara após CADA resposta texto do agente
 *   - Substitui o antigo laos-continuation.ts (que usava session.idle, frágil)
 *   - Decisão do usuário (2026-06-21): usar AMBAS as estratégias de continuação
 *     em cascata: (1) client.session.promptAsync(), (2) tui.prompt.append
 *
 * Arquitetura:
 *   1. experimental.text.complete → detecta pending, decide ação
 *   2. State tracking (.laos/state/completion.json) sobrevive a compaction
 *   3. 3 tentativas de auto-continue → depois, exige justificativa
 *   4. Justificativa insatisfatória → volta pro agente
 *   5. Queda de braço: promptAsync() + tui.prompt.append como fallback garantido
 *   6. Nenhum prompt envolvido — enforcement mecânico no runtime
 *
 * @module laos-completion-gate
 */

import { readFileSync, existsSync, writeFileSync, mkdirSync, readdirSync } from "node:fs"
import { join, resolve, dirname } from "node:path"
import type { Plugin } from "@opencode-ai/plugin"

// ─── Config ─────────────────────────────────────────────────────

const MAX_CONTINUATIONS = 3
const STATE_DIR = ".laos/state"
const STATE_FILE = "completion.json"

// ─── State types ────────────────────────────────────────────────

interface CompletionState {
  project: string
  pendingCount: number
  completedCount: number
  continuationCount: number
  awaitingJustification: boolean
  lastOutputHash: string
  lastJustification: string
  updatedAt: string
}

function defaultState(project: string): CompletionState {
  return {
    project,
    pendingCount: 0,
    completedCount: 0,
    continuationCount: 0,
    awaitingJustification: false,
    lastOutputHash: "",
    lastJustification: "",
    updatedAt: new Date().toISOString(),
  }
}

// ─── In-memory state (sobrevive a tool calls dentro do mesmo turno) ──

let state: CompletionState = defaultState("")
let lastEmittedAction: "continue" | "justify" | "pass" | "blocked" = "pass"

// ─── Persistência ──────────────────────────────────────────────

function persistState(workspaceRoot: string, s: CompletionState): void {
  try {
    const dir = join(workspaceRoot, STATE_DIR)
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
    writeFileSync(join(dir, STATE_FILE), JSON.stringify(s, null, 2), "utf-8")
  } catch {
    // non-critical; state survives in memory
  }
}

function readState(workspaceRoot: string, project: string): CompletionState {
  try {
    const filePath = join(workspaceRoot, STATE_DIR, STATE_FILE)
    if (existsSync(filePath)) {
      const raw = readFileSync(filePath, "utf-8")
      const parsed = JSON.parse(raw) as CompletionState
      if (parsed.project === project) return parsed
    }
  } catch {
    // corrupt or missing
  }
  return defaultState(project)
}

// ─── Todo.md parser ─────────────────────────────────────────────

function countTodos(projectDir: string): { pending: number; completed: number } {
  const paths = [
    join(projectDir, "spec", "todo.md"),
    join(projectDir, "spec", "todos.md"),
    join(projectDir, "todo.md"),
    join(projectDir, "TODO.md"),
  ]

  for (const todoPath of paths) {
    try {
      if (!existsSync(todoPath)) continue
      const content = readFileSync(todoPath, "utf-8")
      const lines = content.split("\n")
      let pending = 0
      let completed = 0
      for (const line of lines) {
        const trimmed = line.trim()
        if (trimmed.startsWith("- [ ]") || trimmed.startsWith("* [ ]")) pending++
        if (trimmed.startsWith("- [x]") || trimmed.startsWith("* [x]")) completed++
      }
      return { pending, completed }
    } catch {
      continue
    }
  }

  // Fallback: project.yaml deliverables
  try {
    const projYaml = join(projectDir, "project.yaml")
    if (existsSync(projYaml)) {
      const content = readFileSync(projYaml, "utf-8")
      const deliverableLines = content.match(/^\s+-\s+\S+/gm) || []
      const deliverables = deliverableLines.length
      let existing = 0
      for (const line of deliverableLines) {
        const artifact = line.trim().replace(/^- /, "").trim()
        if (artifact) {
          const artifactPath = join(projectDir, "artifacts", artifact)
          if (existsSync(artifactPath)) existing++
        }
      }
      const pending = Math.max(0, deliverables - existing)
      return { pending, completed: existing }
    }
  } catch {
    // ignore
  }

  return { pending: 0, completed: 0 }
}

// ─── Simple hash (para detectar loops) ──────────────────────────

function simpleHash(text: string): string {
  let hash = 0
  const sample = text.slice(-500)
  for (let i = 0; i < sample.length; i++) {
    const char = sample.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash |= 0
  }
  return hash.toString(16)
}

// ─── Mecanismos de continuação (DUAS estratégias) ──────────────

/**
 * Opção 1: client.session.promptAsync() — mais controle.
 * Envia texto como um novo prompt ao agente, forçando-o a processar.
 * Só funciona se o SDK expõe promptAsync no client da sessão.
 */
async function tryPromptAsync(client: any, text: string): Promise<boolean> {
  try {
    if (typeof client?.session?.promptAsync === "function") {
      await client.session.promptAsync({ text })
      return true
    }
    return false
  } catch {
    return false
  }
}

/**
 * Opção 2: tui.prompt.append — mais simples, sempre acessível.
 * Dispara evento de UI que preenche o input do usuário.
 * O usuário vê a mensagem e pode dar Enter para submeter.
 * Usa o canal de eventos interno do OpenCode (internal.send).
 */
async function tryTuiPromptAppend(client: any, text: string): Promise<boolean> {
  try {
    // Tenta via internal.send (API canônica do OpenCode Desktop)
    if (typeof client?.internal?.send === "function") {
      await client.internal.send({
        type: "tui.prompt.append",
        payload: { text },
      })
      return true
    }

    // Tenta via client.$emit (API alternativa)
    if (typeof (client as any).$emit === "function") {
      ;(client as any).$emit("tui.prompt.append", { text })
      return true
    }

    return false
  } catch {
    return false
  }
}

/**
 * Dispara AMBOS os mecanismos em cascata.
 * 1º: client.session.promptAsync() — tenta submeter direto
 * 2º: tui.prompt.append — preenche input como fallback garantido
 *
 * Retorna true se PELO MENOS UM funcionou.
 */
async function sendContinuation(client: any, text: string): Promise<boolean> {
  // Tenta Opção 1 (controle total)
  const ok1 = await tryPromptAsync(client, text)
  if (ok1) return true

  // Se Opção 1 falhou, tenta Opção 2 (simples, sempre acessível)
  const ok2 = await tryTuiPromptAppend(client, text)
  return ok2
}

// ─── Sincerity check ────────────────────────────────────────────

function isSincereBlocker(text: string): { sincere: boolean; reason: string } {
  const lower = text.toLowerCase()

  const sincerePatterns: [RegExp, string][] = [
    [/(tool|ferramenta|mcp)\s+(não\s+)?(não\s+existe|não\s+encontrado|não\s+disponível|inexistente|faltando|não\s+tem)/i, "tool_missing"],
    [/(não\s+tenho|não\s+consigo\s+acessar)\s+(a\s+)?(tool|ferramenta|mcp)/i, "tool_no_access"],
    [/API\s*(key|_key)?\s*(não|inválida|missing|expirou|não\s+configurada)/i, "api_key_issue"],
    [/(requires?|precisa\s+de)\s+(payment|pagamento|subscription|plano|upgrade)/i, "requires_payment"],
    [/não\s+(tem|tenho)\s*(acesso|permissão)/i, "no_access"],
    [/not\s+implemented|não\s+implementado|feature\s+(not\s+)?(available|ready)/i, "not_implemented"],
    [/não\s+(existe|encontrado|disponível)\s*(no|no\s+módulo|no\s+sistema|na\s+plataforma)/i, "not_available"],
    [/needs?\s+(manual\s+)?(setup|config|configuration|install|deploy)/i, "needs_setup"],
    [/HITL|human.in.the.loop|manual\s+approval|precisa\s+de\s+(aprovação|revisão)/i, "hitl"],
    [/error\s*\d{3}|HTTP\s*\d{3}|timeout|connection refused/i, "http_error"],
    [/\.env\b|API_KEY|SECRET|config\./i, "env_config"],
    [/: acesso negado|permission denied|unauthorized/i, "denied"],
    [/porque\s+(não\s+)?(depende|requer|precisa|exige)\s+(de\s+)?(um|uma|outro|outra)\s+(sistema|api|ferramenta|dado|pessoa|equipe)/i, "external_dependency"],
  ]

  const handwavyPatterns = [
    /não\s+sei/i,
    /não\s+consigo/i,
    /não\s+é\s+possível/i,
    /é\s+(muito\s+)?(difícil|complexo)/i,
    /acho\s+que/i,
    /talvez/i,
    /não\s+tenho\s+certeza/i,
    /prefiro\s+parar/i,
    /não\s+vale\s+a\s+pena/i,
    /não\s+precisa/i,
    /já\s+está\s+bom/i,
    /não\s+precisa\s+completar/i,
    /não\s+tem\s+importância/i,
    /é\s+desnecessário/i,
  ]

  const foundSincere: string[] = []
  for (const [pattern, label] of sincerePatterns) {
    if (pattern.test(lower)) foundSincere.push(label)
  }

  const foundHandwavy = handwavyPatterns.some(p => p.test(lower))

  if (foundSincere.length >= 1) {
    return { sincere: true, reason: `bloqueador real: ${foundSincere.join(", ")}` }
  }

  if (foundHandwavy) {
    return { sincere: false, reason: "justificativa genérica sem bloqueador real" }
  }

  return { sincere: false, reason: "nenhum bloqueador concreto mencionado" }
}

// ─── Resolve project ────────────────────────────────────────────

function resolveProject(directory: string): { projectDir: string; projectName: string } | null {
  const projectsMatch = directory.match(/[\\/]projects[\\/]([^\\/]+)/)
  if (projectsMatch) {
    const name = projectsMatch[1]
    const root = directory.split(/[\\/]projects[\\/]/)[0]
    return { projectDir: join(root, "projects", name), projectName: name }
  }

  if (existsSync(join(directory, "spec", "todo.md"))) {
    return { projectDir: directory, projectName: directory.split(/[\\/]/).pop() || "unknown" }
  }

  try {
    const projectsDir = join(directory, "projects")
    if (existsSync(projectsDir)) {
      const dirs = readdirSync(projectsDir, { withFileTypes: true })
      for (const dir of dirs) {
        if (dir.isDirectory() && !dir.name.startsWith("_")) {
          if (existsSync(join(projectsDir, dir.name, "spec", "todo.md"))) {
            return { projectDir: join(projectsDir, dir.name), projectName: dir.name }
          }
        }
      }
    }
  } catch { /* ignore */ }

  return null
}

// ─── Mensagens ──────────────────────────────────────────────────

function buildContinueMessage(pending: number, completed: number): string {
  return (
    `[Continuação automática — Completion Gate]\n` +
    `Ainda há ${pending} tarefa(s) pendente(s) (${completed} concluída(s)).\n` +
    `Continue trabalhando até completar todas.\n` +
    `Se encontrar um bloqueador real (tool inexistente, dependência externa, ` +
    `erro de API, pagamento necessário), explique o motivo ESPECÍFICO na sua ` +
    `resposta. Respostas genéricas serão rejeitadas.`
  )
}

function buildJustifyMessage(pending: number, completed: number): string {
  return (
    `[Completion Gate — Justificativa necessária]\n` +
    `Após ${MAX_CONTINUATIONS} tentativas, ainda há ${pending} tarefa(s) pendente(s) ` +
    `(${completed} concluída(s)).\n\n` +
    `VOCÊ DEVE JUSTIFICAR por que não pode continuar. Seja específico:\n` +
    `- Qual ferramenta está faltando?\n` +
    `- Qual dependência externa precisa?\n` +
    `- Qual erro ocorreu?\n` +
    `- Precisa de pagamento / permissão / setup manual?\n\n` +
    `Respostas genéricas como "não sei", "não consigo", "é difícil" serão ` +
    `rejeitadas e você continuará trabalhando.\n` +
    `Se NÃO houver bloqueador real, apenas continue trabalhando.`
  )
}

function buildRejectMessage(): string {
  return (
    `[Completion Gate — Justificativa rejeitada]\n` +
    `A justificativa não contém um bloqueador real específico. ` +
    `Menções genéricas sem ferramenta, erro ou dependência concreta ` +
    `não são aceitas.\n` +
    `Continue trabalhando nas tarefas pendentes. Se houver um bloqueador ` +
    `real, descreva-o com detalhes (qual tool, qual erro, qual dependência).`
  )
}

// ─── Plugin export ──────────────────────────────────────────────

export const LaosCompletionGate: Plugin = async ({ client, directory }) => {
  // Inicializa estado
  const projectInfo = resolveProject(directory)
  if (projectInfo) {
    state = readState(directory, projectInfo.projectName)
    state.project = projectInfo.projectName
  }

  return {
    // ─── Hook principal: após CADA resposta texto ────────────
    "experimental.text.complete": async (input, output) => {
      const projectInfo = resolveProject(directory)
      if (!projectInfo) return

      const { projectDir, projectName } = projectInfo

      // 1. Conta tarefas
      const { pending, completed } = countTodos(projectDir)
      state.pendingCount = pending
      state.completedCount = completed
      state.updatedAt = new Date().toISOString()

      // 2. Detecta loop (mesmo texto se repetindo)
      const hash = simpleHash(output.text)
      if (hash === state.lastOutputHash && pending > 0 && state.continuationCount > 0) {
        const msg = buildContinueMessage(pending, completed)
        output.text += `\n\n---\n${msg}`
        state.lastOutputHash = hash
        lastEmittedAction = "continue"
        await sendContinuation(client, msg)
        persistState(directory, state)
        return
      }
      state.lastOutputHash = hash

      // 3. Sem pendências → libera
      if (pending === 0) {
        state.continuationCount = 0
        state.awaitingJustification = false
        state.lastJustification = ""
        persistState(directory, state)
        lastEmittedAction = "pass"
        return
      }

      // 4. Aguardando justificativa (após 3 tentativas)
      if (state.awaitingJustification) {
        const analysis = isSincereBlocker(output.text)

        if (analysis.sincere) {
          output.text += `\n\n---\n[Gate] ✅ Bloqueador real aceito: ${analysis.reason}`
          state.continuationCount = 0
          state.awaitingJustification = false
          state.lastJustification = output.text.slice(-300)
          persistState(directory, state)
          lastEmittedAction = "blocked"
          return
        }

        // Justificativa fraca → rejeita e manda continuar
        const msg = buildRejectMessage()
        output.text += `\n\n---\n${msg}`
        state.lastJustification = output.text.slice(-300)
        persistState(directory, state)
        lastEmittedAction = "continue"

        // Dispara AMBAS as estratégias de continuação
        await sendContinuation(client, msg)
        return
      }

      // 5. Fluxo normal
      state.continuationCount++

      if (state.continuationCount >= MAX_CONTINUATIONS) {
        // Esgotou tentativas → exige justificativa
        const msg = buildJustifyMessage(pending, completed)
        output.text += `\n\n---\n${msg}`
        state.awaitingJustification = true
        persistState(directory, state)
        lastEmittedAction = "justify"
        // Dispara continuação com o pedido de justificativa
        await sendContinuation(client, msg)
        return
      }

      // Ainda tem tentativas → continua automaticamente
      const msg = buildContinueMessage(pending, completed)
      output.text += `\n\n---\n${msg}`

      // Dispara AMBAS as estratégias de continuação
      await sendContinuation(client, msg)

      persistState(directory, state)
      lastEmittedAction = "continue"
    },

    // ─── Preserva estado na compactação ──────────────────────
    "experimental.session.compacting": async (_input, output) => {
      if (state.project) {
        output.context.push(
          `[LAOS Completion Gate] Projeto: ${state.project}`,
          `  Pending: ${state.pendingCount} | Completed: ${state.completedCount}`,
          `  Continuation: ${state.continuationCount}/${MAX_CONTINUATIONS}`,
          `  Awaiting justification: ${state.awaitingJustification}`,
          `  Last action: ${lastEmittedAction}`,
        )
      }
    },
  }
}
