#!/usr/bin/env bash
#
# PreToolUse gate hook (Claude Code, matcher: Bash).
#
# Lê o payload JSON do hook via stdin e recusa (exit 2) comandos
# destrutivos óbvios antes de rodarem — mesmo espírito do
# .githooks/pre-push deste repositório (recusa push direto/force em
# main), estendido para o próprio shell do agente.
#
# Falha aberta de propósito: se o payload não tiver o campo esperado,
# deixa passar em vez de travar o agente por um formato inesperado.
#
# Avalia cada subcomando isolado (divisão textual por &&, ||, ;, | e
# quebra de linha; `git -C <caminho>` normalizado para `git`), com os
# padrões ancorados no início do segmento — ver SDD-DTF-0021.
set -euo pipefail

payload="$(cat)"
segments="$(python3 -c '
import json, re, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
command = data.get("tool_input", {}).get("command", "")
for s in re.split(r"&&|\|\||;|\||\n", command):
    s = re.sub(r"^git\s+-C\s+\S+\s+", "git ", s.strip())
    if s:
        print(s)
' <<<"$payload")"

[ -z "$segments" ] && exit 0

deny() {
  echo "guard_bash: bloqueado — $1" >&2
  exit 2
}

while IFS= read -r segment; do
  case "$segment" in
    "git push"*--force*|"git push"*" -f"|"git push"*" -f "*)
      deny "force-push detectado. Use PR normal." ;;
    "git push"*" main"|"git push"*" main "*|"git push"*":main"*|"git push"*" main:"*)
      deny "push direto em main. Abra PR." ;;
    "git reset --hard"*)
      deny "reset --hard é destrutivo. Confirme com o usuário antes." ;;
    "rm -rf ."*|"rm -rf /"*|"rm -rf ~"*)
      deny "rm -rf de escopo amplo. Confirme com o usuário antes." ;;
  esac
done <<<"$segments"

exit 0
