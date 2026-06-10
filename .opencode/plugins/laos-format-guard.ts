/**
 * FormatGuard — Advisory formatting hygiene plugin for LAOS.
 *
 * Provenance: LAOS-specific (not from OmO directly). Addresses the pattern
 * where agents produce inconsistent formatting — mixed tabs/spaces, missing
 * final newlines, trailing whitespace, CRLF in scripts that expect LF, etc.
 *
 * Checks performed (advisory — warn only, never blocks a write):
 * 1. Trailing whitespace on any line
 * 2. Missing final newline at end of file
 * 3. Mixed indentation (tabs AND spaces at line start) within the same file
 * 4. Tab indentation in .py files (Python convention: spaces only)
 * 5. CRLF line endings in .py, .sh, .yaml, .yml files (should use LF)
 *
 * CRLF in .ts, .js, .json, .md files is OK on Windows (no warning).
 *
 * Hook: tool.execute.after on Write and Edit tools.
 */

export const FormatGuard = async ({
  project,
  client,
  $,
  directory,
  worktree,
}: {
  project: string
  client: any
  $: any
  directory: string
  worktree: string
}) => {
  const LF_ONLY_EXTENSIONS = new Set([".py", ".sh", ".yaml", ".yml"])
  const PYTHON_EXTENSIONS = new Set([".py"])

  function getExtension(filePath: string): string {
    const lastDot = filePath.lastIndexOf(".")
    if (lastDot === -1) return ""
    return filePath.slice(lastDot).toLowerCase()
  }

  function checkContent(content: string, filePath: string): string[] {
    const warnings: string[] = []
    const ext = getExtension(filePath)

    // Missing final newline
    if (content.length > 0 && !content.endsWith("\n")) {
      warnings.push(`[FormatGuard] Missing final newline in ${filePath}`)
    }

    // CRLF check for LF-only file types
    if (LF_ONLY_EXTENSIONS.has(ext) && content.includes("\r\n")) {
      warnings.push(
        `[FormatGuard] CRLF line endings found in ${filePath} — ${ext} files should use LF`,
      )
    }

    const lines = content.split(/\r?\n/)
    let hasTabIndent = false
    let hasSpaceIndent = false

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]

      // Trailing whitespace (skip empty lines)
      if (line.length > 0 && line !== line.trimEnd()) {
        warnings.push(`[FormatGuard] Trailing whitespace on line ${i + 1} in ${filePath}`)
      }

      // Indentation analysis — only for lines that start with whitespace
      const indentMatch = line.match(/^([\t ]+)\S/)
      if (indentMatch) {
        const indent = indentMatch[1]
        if (indent.includes("\t")) hasTabIndent = true
        if (indent.includes(" ")) hasSpaceIndent = true
      }
    }

    // Mixed indentation in the same file
    if (hasTabIndent && hasSpaceIndent) {
      warnings.push(`[FormatGuard] Mixed indentation (tabs and spaces) in ${filePath}`)
    }

    // Tab indentation in Python files
    if (PYTHON_EXTENSIONS.has(ext) && hasTabIndent) {
      warnings.push(
        `[FormatGuard] Tab indentation in ${filePath} — Python files must use spaces (PEP 8)`,
      )
    }

    return warnings
  }

  return {
    "tool.execute.after": async (input: any, output: any) => {
      try {
        const toolName = input?.tool
        if (toolName !== "write" && toolName !== "edit") return output

        const args = output?.args
        if (!args) return output

        const filePath: string | undefined = args.filePath || args.path || args.file
        const content: string | undefined = args.content || args.newString || args.text

        if (!filePath || typeof content !== "string") return output

        const warnings = checkContent(content, filePath)
        if (warnings.length === 0) return output

        const resultStr =
          typeof output?.result === "string"
            ? output.result
            : JSON.stringify(output?.result ?? "")
        const separator = resultStr.length > 0 ? "\n" : ""

        output.result = resultStr + separator + warnings.join("\n")
      } catch {
        // Never break a write — this plugin is advisory only
      }

      return output
    },
  }
}
