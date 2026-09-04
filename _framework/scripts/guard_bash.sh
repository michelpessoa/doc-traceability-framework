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
set -euo pipefail

payload="$(cat)"
command="$(python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print(data.get("tool_input", {}).get("command", ""))
' <<<"$payload")"

[ -z "$command" ] && exit 0

deny() {
  echo "guard_bash: bloqueado — $1" >&2
  exit 2
}

case "$command" in
  *"push --force"*|*"push -f "*|*"push -f"|*" -f "*"origin main"*)
    deny "force-push detectado. Use PR normal." ;;
  *"push"*"origin main"*|*"push"*" main"*)
    deny "push direto em main. Abra PR." ;;
  *"reset --hard"*)
    deny "reset --hard é destrutivo. Confirme com o usuário antes." ;;
  *"rm -rf ."*|*"rm -rf /"*|*"rm -rf ~"*)
    deny "rm -rf de escopo amplo. Confirme com o usuário antes." ;;
esac

exit 0
