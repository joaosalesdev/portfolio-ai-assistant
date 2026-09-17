# Inventário dos exemplos editáveis

## Fontes do RAG

Todos os arquivos abaixo estão em `knowledge/documents/` e possuem uma entrada
desabilitada em `knowledge/manifest.yaml`:

| Arquivo | Preenchimento |
| --- | --- |
| `profile-template.md` | Perfil/currículo público |
| `project-template.md` | Modelo reutilizável de projeto |
| `melita.md` | Projeto Melita |
| `salesforce.md` | Integração Salesforce sanitizada |
| `automations.md` | Caso de automação |
| `italian-saas.md` | Plataforma SaaS de italiano |
| `portfolio.md` | Conteúdo público do portfólio |
| `github-readme.md` | Documentação selecionada de um repositório público |
| `portfolio-ai-assistant.md` | Estado real deste projeto |

Os títulos identificam temas a documentar, não comprovam experiência. Substitua
placeholders por informações verificadas antes de aprovar. Não aprove modelos
genéricos sem conteúdo nem duplique documentos desnecessariamente.

## Documentação e avaliação

- `docs/architecture.md`: arquitetura e decisões pendentes.
- `docs/adr/template.md`: modelo para futuras decisões.
- `docs/experiments/template.md`: hipótese, configuração e resultados.
- `docs/production-log.md`: modelo sem acontecimentos de produção registrados.
- `docs/runbook.md`: procedimentos ainda a implementar e validar.
- `evals/datasets/questions.example.json`: casos desabilitados para anotação.
- `evals/reports/template.md`: relatório sem métricas inventadas.
- `infra/README.md`: checklist dos artefatos de infraestrutura futuros.
- `migrations/README.md`: decisões necessárias para migrations reais.
- `tests/integration/README.md` e `tests/security/README.md`: casos a implementar.
- `.env.example`: nomes de configuração, sem valores secretos.

## Arquivos locais ignorados

`knowledge/raw/README.local.md` e `knowledge/private/README.local.md` explicam o
uso das pastas locais. Por estarem ignorados, não estarão presentes em novos clones.
O comportamento está descrito também no README público de `knowledge/`.

## Limite destes exemplos

Ainda não existem handlers, Dockerfiles, compose, workflow de deploy ou integração
com embeddings/pgvector. Eles serão implementados em etapas, com validação, em vez
de arquivos vazios que aparentem executar um pipeline completo. Os modelos desta
lista cobrem o conteúdo editável inicial, não uma aplicação concluída.
