# Incidentes e postmortem

Fluxo separado do funil principal — nunca abra uma RFC para tratar um
incidente em andamento.

1. Crie um `INC` com severidade objetiva (`workflow-rules.yaml:severity_scale`: SEV1/SEV2 exigem postmortem
   completo, SEV3 leve, SEV4 opcional).
2. Regra de recorrência: mesma causa raiz (`root_cause_key`) repetida em
   até 90 dias torna o postmortem obrigatório mesmo em SEV4.
3. Ao fechar o incidente, crie o `PM` (`source_incident` aponta para o
   INC) com os action items.
4. Triagem de cada action item (`workflow-rules.yaml:action_item_triage`): ajuste pontual sem nenhum critério do
   gate → SPEC direto, sem RFC; mudança estrutural (atenderia a
   algum critério do gate RFC→ADR) → nova RFC (`relates_to` aponta para
   o PM), seguindo o fluxo normal a partir daí.
