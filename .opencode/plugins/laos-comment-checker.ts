/**
 * CommentChecker — OpenCode plugin that detects AI slop in net-new comments.
 *
 * Provenance:
 *   - OmO `packages/comment-checker-core/` (feature #10 in knowledge/omo-adoption-provenance.md)
 *   - LAOS extension: synthetic data frontmatter violation detection (Hard Rule #11 overlap
 *     with laos-guards, but this is comment-level detection, not file-level blocking).
 *
 * Hook: `tool.execute.after` on Write and Edit tools only.
 * Behavior: advisory — appends WARNING to tool output, does NOT block the write.
 *
 * Slop patterns detected:
 *   1. Placeholder comments: "Add your code here", "TODO: implement this function"
 *   2. Template comments: "This is where you...", "Here will be..."
 *   3. Trivially obvious comments: "set x to 5", "initialize the variable"
 *   4. Redundant summary comments: >80% word overlap with the next code line
 *   5. Synthetic data frontmatter violations (Hard Rule #11): comments referencing
 *      synthetic/fabricated data without required frontmatter markers
 *
 * @module laos-comment-checker
 */

export const CommentChecker = async ({ project, client, $, directory, worktree }) => {
  const PLACEHOLDER_PATTERN =
    /(?:\/\/|#)\s*(?:add|insert|put|place|write|implement|todo|fixme|hack|xxx)\s+(?:your|the|a|this)\s+(?:code|logic|implementation|function|method|value|variable)/i;

  const TEMPLATE_PATTERN =
    /(?:\/\/|#)\s*(?:this|here)\s+(?:is|will|should)\s+(?:where|be|contain)/i;

  const TRIVIAL_PATTERN =
    /(?:\/\/|#)\s*(?:set|initialize|assign|define|create|declare|update|increment|decrement|reset|return|print|log|call|invoke|execute|run|start|stop|check|validate|verify|ensure|make)\s+\w+\s+(?:to|into|as|with|for|from|by|at|in|on)\s+/i;

  const SYNTHETIC_DATA_PATTERN =
    /(?:\/\/|#)\s*(?:synthetic|fabricated|mock|fake|dummy|sample|generated)\s*(?:data|values|records|rows|entries|dataset)/i;

  const SYNTHETIC_FRONTMATTER_MISSING =
    /synthetic:\s*true/;

  const COMMENT_PREFIX = /^\s*(?:(?:\/\/|#|--)|\/\*|<!--)/;

  function extractCommentText(line: string): string | null {
    const match = line.match(/^\s*(?:(?:\/\/|#|--)\s*|\/\*\s*|<!--\s*)(.*)/);
    if (!match) return null;
    let text = match[1];
    text = text.replace(/\s*(?:\*\/|-->)\s*$/, "");
    return text.trim();
  }

  function wordOverlap(a: string, b: string): number {
    const wordsA = new Set(a.toLowerCase().split(/\s+/).filter(Boolean));
    const wordsB = new Set(b.toLowerCase().split(/\s+/).filter(Boolean));
    if (wordsA.size === 0 || wordsB.size === 0) return 0;
    let intersection = 0;
    for (const w of wordsA) {
      if (wordsB.has(w)) intersection++;
    }
    return intersection / Math.min(wordsA.size, wordsB.size);
  }

  function detectSlop(
    content: string
  ): { line: number; text: string; reason: string }[] {
    const findings: { line: number; text: string; reason: string }[] = [];
    const lines = content.split("\n");

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!COMMENT_PREFIX.test(line)) continue;

      const commentText = extractCommentText(line);
      if (!commentText || commentText.length < 5) continue;

      if (PLACEHOLDER_PATTERN.test(line)) {
        findings.push({
          line: i + 1,
          text: commentText,
          reason: "placeholder comment",
        });
        continue;
      }

      if (TEMPLATE_PATTERN.test(line)) {
        findings.push({
          line: i + 1,
          text: commentText,
          reason: "template comment",
        });
        continue;
      }

      if (TRIVIAL_PATTERN.test(line)) {
        findings.push({
          line: i + 1,
          text: commentText,
          reason: "trivially obvious comment",
        });
        continue;
      }

      if (SYNTHETIC_DATA_PATTERN.test(line)) {
        const fullContent = content;
        const hasFrontmatter = SYNTHETIC_FRONTMATTER_MISSING.test(fullContent);
        if (!hasFrontmatter) {
          findings.push({
            line: i + 1,
            text: commentText,
            reason:
              "synthetic data reference without frontmatter (Hard Rule #11 violation)",
          });
        }
        continue;
      }

      if (i + 1 < lines.length) {
        const nextLine = lines[i + 1];
        if (nextLine && !COMMENT_PREFIX.test(nextLine) && nextLine.trim().length > 0) {
          const overlap = wordOverlap(commentText, nextLine.replace(/\/\/.*$/, "").trim());
          if (overlap > 0.8) {
            findings.push({
              line: i + 1,
              text: commentText,
              reason: `redundant summary (>${Math.round(overlap * 100)}% word overlap with next line)`,
            });
            continue;
          }
        }
      }
    }

    return findings;
  }

  return {
    "tool.execute.after": async (input, output) => {
      const toolName = input?.tool?.name || input?.tool || "";
      if (toolName !== "write" && toolName !== "edit") return output;

      const result = output?.result;
      if (!result) return output;

      let content = "";
      if (typeof result === "string") {
        content = result;
      } else if (result?.content && typeof result.content === "string") {
        content = result.content;
      } else if (result?.args?.content && typeof result.args.content === "string") {
        content = result.args.content;
      } else {
        try {
          content = JSON.stringify(result);
        } catch {
          return output;
        }
      }

      const slop = detectSlop(content);
      if (slop.length === 0) return output;

      const warningLines = slop.map(
        (f) => `  L${f.line}: "${f.text}" — ${f.reason}`
      );
      const warning =
        `\n\n⚠️ CommentChecker: AI slop detected (${slop.length} issue${slop.length > 1 ? "s" : ""}):\n` +
        warningLines.join("\n") +
        `\nAdvisory only — review and remove unnecessary comments.`;

      if (typeof result === "string") {
        output.result = result + warning;
      } else if (result && typeof result === "object") {
        if (typeof result.content === "string") {
          result.content = result.content + warning;
        } else {
          result._commentCheckerWarning = warning;
        }
      }

      return output;
    },
  };
};
