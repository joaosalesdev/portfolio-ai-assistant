# Migrações — modelo de planejamento

Nenhuma migration executável existe ainda. Antes da primeira, preencher:

- Modelo e dimensão dos embeddings: [a definir]
- Versão PostgreSQL/pgvector: [a definir]
- Ferramenta de migração: [a definir]
- Tabelas: documents, chunks, index_profiles e ingestion_runs.
- Restrições: identidade de fonte única, referências e exclusão dos chunks.
- Atualização: substituir a versão ativa atomicamente após gerar embeddings.
- Validação: aplicação em banco vazio, integridade e recuperação após falha.

Não adicionar dumps de bancos reais ou credenciais às migrations.
