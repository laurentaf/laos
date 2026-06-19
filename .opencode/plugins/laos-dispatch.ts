/**
 * LAOS Dispatch — Agentic Framework Mode Router
 *
 * Provenance:
 *   - User requirement: "was a requisite for LAOS, I don't know why it's not implemented"
 *   - OmO Team Mode: src/features/team-mode/ (git worktrees, mailbox, tmux)
 *   - LAOS projects: previsao-concursos (9 needs, 4 capabilities — prime parallel candidate)
 *   - User decision: Empirical Consensus for model evaluation (3-5 models, evaluator picks best)
 *   - User decision: Consensus = Governance (LACOUNCIL voting) + Empirical (evaluator picks)
 *   - User decision: Parallel = OmO-style (git worktrees + mailbox + tmux)
 *
 * Three dispatch modes:
 *
 *   1. SEQUENTIAL (default, current LAOS behavior)
 *      One specialist at a time. Each stage completes before the next begins.
 *      Use when: stages have hard dependencies (data model → dashboard → automation).
 *
 *   2. PARALLEL (new — OmO-style)
 *      Multiple independent specialists run simultaneously using git worktrees.
 *      Each member gets a worktree, communicates via mailbox protocol.
 *      Use when: deliverables are independent (data model + design can run in parallel).
 *      Architecture: lead (orchestrator) + 1-8 members (specialist subagents),
 *      each in their own worktree, coordinated via mailbox files.
 *
 *   3. CONSENSUS (new — two sub-modes)
 *      a. GOVERNANCE: LACOUNCIL voting (existing). Each Conselho member votes,
 *         tally determines outcome. Use for structural decisions.
 *      b. EMPIRICAL: N agents produce solutions independently, then a domain-specific
 *         evaluator picks the best. Use for model selection, design comparison.
 *         Evaluators: chief-data-scientist (model fit, R²/AIC),
 *                     chief-designer (visual hierarchy, accessibility),
 *                     chief-engineer (reliability, SLA compliance).
 *
 * This plugin provides:
 *   - A custom tool `laos-dispatch` that the orchestrator uses to dispatch
 *     specialists with mode selection.
 *   - Session state tracking for active dispatches.
 *   - Mailbox protocol for parallel mode coordination.
 */

import type { Plugin } from "@opencode-ai/plugin"

type DispatchMode = "sequential" | "parallel" | "consensus"
type ConsensusSubMode = "governance" | "empirical"

interface DispatchPlan {
  mode: DispatchMode
  consensusSubMode?: ConsensusSubMode
  projectId: string
  planId: string
  members: DispatchMember[]
  evaluator?: string // For empirical consensus
  status: "pending" | "running" | "evaluating" | "completed"
}

interface DispatchMember {
  agent: string
  task: string
  worktree?: string // For parallel mode
  mailboxPath?: string
  status: "pending" | "running" | "completed" | "failed" | "timed_out"
  result?: any
  timeout_min?: number       // TD-5: max execution time in minutes
  started_at?: number        // TD-5: unix ms when dispatch started
  retry_count?: number       // TD-2: how many retries attempted (max retry_limit)
  retry_limit?: number       // TD-2: max auto-retries (default 2)
  last_error_class?: string  // TD-2: error_class from compact receipt for routing
}

interface MailboxMessage {
  from: string
  to: string
  type: "status" | "artifact" | "blocker" | "done"
  payload: any
  timestamp: string
}

// Session-level dispatch state
const activeDispatches: Map<string, DispatchPlan> = new Map()

export const LaosDispatch = async ({ project, directory, $, worktree }: {
  project: string
  directory: string
  $: any
  worktree?: string
}) => {
  return {
    // ─── Custom tool: laos-dispatch ─────────────────────────────
    tool: {
      "laos-dispatch": {
        description:
          "Dispatch LAOS specialists using the specified agentic framework mode. " +
          "Modes: sequential (one at a time), parallel (simultaneous with worktrees), " +
          "consensus (governance voting or empirical evaluation).",
        args: {
          mode: {
            type: "string" as const,
            enum: ["sequential", "parallel", "consensus"],
            description: "Dispatch mode",
          },
          consensusSubMode: {
            type: "string" as const,
            enum: ["governance", "empirical"],
            description: "Consensus sub-mode (only for consensus mode)",
          },
          projectId: {
            type: "string" as const,
            description: "Project name from projects/<name>/project.yaml",
          },
          planId: {
            type: "string" as const,
            description: "WDL plan ID (from verdict.yaml)",
          },
          members: {
            type: "array" as const,
            items: {
              type: "object" as const,
              properties: {
                agent: { type: "string" as const },
                task: { type: "string" as const },
                timeout_min: { type: "number" as const },
                retry_limit: { type: "number" as const },
              },
            },
            description: "List of {agent, task} dispatches with optional timeout_min (TD-5) and retry_limit (TD-2)",
          },
          evaluator: {
            type: "string" as const,
            enum: ["chief-data-scientist", "chief-designer", "chief-engineer"],
            description: "Evaluator for empirical consensus",
          },
        },
        async execute(args: {
          mode: DispatchMode
          consensusSubMode?: ConsensusSubMode
          projectId: string
          planId: string
          members: Array<{ agent: string; task: string }>
          evaluator?: string
        }, context: any) {
          const { mode, projectId, planId, members, consensusSubMode, evaluator } = args

          // ─── Validation ──────────────────────────────────────────
          if (mode === "consensus" && !consensusSubMode) {
            return "ERROR: consensus mode requires consensusSubMode (governance or empirical)"
          }
          if (mode === "consensus" && consensusSubMode === "empirical" && !evaluator) {
            return "ERROR: empirical consensus requires an evaluator " +
                   "(chief-data-scientist, chief-designer, or chief-engineer)"
          }
          if (members.length === 0) {
            return "ERROR: at least one member is required"
          }
          if (mode === "parallel" && members.length > 8) {
            return "ERROR: parallel mode supports max 8 members (plus 1 lead)"
          }

          // ─── Create dispatch plan ────────────────────────────────
          const dispatchPlan: DispatchPlan = {
            mode,
            consensusSubMode,
            projectId,
            planId,
            members: members.map(m => ({
              agent: m.agent,
              task: m.task,
              status: "pending" as const,
              timeout_min: (m as any).timeout_min || 30,     // TD-5: default 30min
              retry_count: 0,                                 // TD-2: start at 0
              retry_limit: (m as any).retry_limit || 2,       // TD-2: max 2 auto-retries
              started_at: Date.now(),                         // TD-5: timestamp
            })),
            evaluator,
            status: "pending",
          }

          activeDispatches.set(planId, dispatchPlan)

          // ─── Mode-specific execution plan ────────────────────────
          switch (mode) {
            case "sequential": {
              return formatSequentialPlan(dispatchPlan)
            }
            case "parallel": {
              return formatParallelPlan(dispatchPlan, directory)
            }
            case "consensus": {
              if (consensusSubMode === "governance") {
                return formatGovernancePlan(dispatchPlan)
              }
              if (consensusSubMode === "empirical") {
                return formatEmpiricalPlan(dispatchPlan, evaluator!)
              }
              return "ERROR: unknown consensus sub-mode"
            }
            default:
              return `ERROR: unknown mode ${mode}`
          }
        },
      },
    },

    // ─── Event: session.idle → check for pending dispatches ─────
    event: async ({ event }: { event: any }) => {
      if (event.type === "session.idle") {
        const now = Date.now()
        for (const [planId, plan] of activeDispatches) {
          // ─── TD-5: Supervisor timeout check ────────────────
          for (const member of plan.members) {
            if (member.status === "running" && member.timeout_min && member.started_at) {
              const elapsed = (now - member.started_at) / 60000 // minutes
              if (elapsed > member.timeout_min) {
                member.status = "timed_out"
                member.result = {
                  error_class: "timeout",
                  summary: `Member ${member.agent} exceeded ${member.timeout_min}min timeout (elapsed: ${elapsed.toFixed(1)}min)`,
                  timeout_min: member.timeout_min,
                  elapsed_min: elapsed,
                  plan_id: planId,
                }
              }
            }
          }

          // ─── TD-2: Auto-retry check for timed_out members ──
          for (const member of plan.members) {
            if (member.status === "timed_out" && member.retry_count! < member.retry_limit!) {
              member.retry_count!++
              member.status = "pending"
              member.started_at = Date.now()
              // In a full implementation, this would re-dispatch
              // the member with the timeout context attached.
            }
          }

          // ─── Parallel mode mailbox check ───────────────────
          if (plan.mode === "parallel" && plan.status === "running") {
            // In a full implementation, this would check mailbox files
            // for completion signals from worktree-based members.
            // For now, this is a placeholder for the mailbox protocol.
          }
        }
      }
    },
  }
}

// ─── Plan formatters ────────────────────────────────────────────

function formatSequentialPlan(plan: DispatchPlan): string {
  const steps = plan.members
    .map((m, i) => `${i + 1}. Dispatch ${m.agent}: ${m.task}`)
    .join("\n")

  return (
    `SEQUENTIAL DISPATCH PLAN\n` +
    `Project: ${plan.projectId}\n` +
    `Plan: ${plan.planId}\n` +
    `Mode: Sequential\n\n` +
    `Steps:\n${steps}\n\n` +
    `Each specialist dispatches AFTER the previous one completes.\n` +
    `Use the task tool to dispatch each specialist in order.\n` +
    `Status: READY — orchestrator should execute these dispatches sequentially.`
  )
}

function formatParallelPlan(plan: DispatchPlan, projectDir: string): string {
  const memberPlans = plan.members
    .map((m, i) => {
      const worktreeName = `${plan.projectId}-${m.agent}-${i}`
      const mailboxPath = `${projectDir}/.laos/mailbox/${worktreeName}`
      return (
        `Member ${i + 1}: ${m.agent}\n` +
        `  Task: ${m.task}\n` +
        `  Worktree: .worktrees/${worktreeName}\n` +
        `  Mailbox: ${mailboxPath}\n` +
        `  Status: pending`
      )
    })
    .join("\n\n")

  return (
    `PARALLEL DISPATCH PLAN\n` +
    `Project: ${plan.projectId}\n` +
    `Plan: ${plan.planId}\n` +
    `Mode: Parallel (OmO-style)\n` +
    `Lead: orchestrator\n` +
    `Members: ${plan.members.length}\n\n` +
    `${memberPlans}\n\n` +
    `COORDINATION PROTOCOL:\n` +
    `1. Create worktrees: git worktree add .worktrees/<name> -b <name>\n` +
    `2. Each member works in their worktree independently\n` +
    `3. Members write status to their mailbox: ${projectDir}/.laos/mailbox/\n` +
    `4. Lead checks mailboxes on session.idle events\n` +
    `5. When all members signal "done", lead merges worktrees\n` +
    `6. Mailbox message format: {from, to, type, payload, timestamp}\n\n` +
    `Status: READY — orchestrator should set up worktrees and dispatch members.`
  )
}

function formatGovernancePlan(plan: DispatchPlan): string {
  return (
    `CONSENSUS DISPATCH PLAN (GOVERNANCE)\n` +
    `Project: ${plan.projectId}\n` +
    `Plan: ${plan.planId}\n` +
    `Mode: Consensus — Governance (LACOUNCIL)\n\n` +
    `PROTOCOL:\n` +
    `1. Orchestrator creates a LACOUNCIL proposal (lacouncil.create_proposal)\n` +
    `2. Each Conselho member votes via lacouncil.register_vote:\n` +
    `   - data-architect\n` +
    `   - dashboard-designer\n` +
    `   - automation-engineer\n` +
    `   - delivery-reviewer\n` +
    `3. lacouncil.tally_votes determines outcome\n` +
    `4. If approved → implement; if rejected → revise proposal\n\n` +
    `This is the EXISTING LACOUNCIL governance flow.\n` +
    `The dispatch plugin formalizes it as a first-class mode.\n\n` +
    `Status: READY — orchestrator should create the proposal and convoke Conselho.`
  )
}

function formatEmpiricalPlan(plan: DispatchPlan, evaluator: string): string {
  const candidates = plan.members
    .map((m, i) => `  Candidate ${i + 1}: ${m.agent} → ${m.task}`)
    .join("\n")

  const evaluatorCriteria: Record<string, string> = {
    "chief-data-scientist":
      "Model fit (R², adjusted R², AIC/BIC), residual diagnostics " +
      "(normality, heteroscedasticity, autocorrelation), prediction accuracy " +
      "(RMSE, MAE, out-of-sample), interpretability (SHAP values, coefficient stability)",
    "chief-designer":
      "Visual hierarchy, accessibility (WCAG 2.1 AA), consistency with DESIGN.md, " +
      "typography readability, color contrast ratios, responsive behavior, " +
      "interaction patterns, anti-slop signals",
    "chief-engineer":
      "Reliability (error handling, graceful degradation), SLA compliance, " +
      "test coverage, performance benchmarks, dependency freshness, " +
      "operational runbook completeness, rollback feasibility",
  }

  return (
    `CONSENSUS DISPATCH PLAN (EMPIRICAL)\n` +
    `Project: ${plan.projectId}\n` +
    `Plan: ${plan.planId}\n` +
    `Mode: Consensus — Empirical Evaluation\n` +
    `Evaluator: ${evaluator}\n\n` +
    `CANDIDATES:\n${candidates}\n\n` +
    `PROTOCOL:\n` +
    `1. Dispatch all candidates IN PARALLEL (they're independent)\n` +
    `2. Each candidate produces their solution independently\n` +
    `3. All solutions are collected and presented to the evaluator\n` +
    `4. Evaluator (${evaluator}) selects the best solution based on:\n` +
    `   ${evaluatorCriteria[evaluator] || "domain-specific criteria"}\n` +
    `5. Winning solution is adopted; others are archived with rationale\n\n` +
    `Status: READY — orchestrator should dispatch all candidates simultaneously,\n` +
    `then present results to the evaluator for selection.`
  )
}
