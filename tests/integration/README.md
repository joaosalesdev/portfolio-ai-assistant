# Casos de integração a implementar

Não há testes de integração implementados nesta pasta.

- Persistir documento e recuperar seus chunks em PostgreSQL com pgvector.
- Ignorar conteúdo e configuração inalterados.
- Substituir chunks sem deixar versões parciais após falha.
- Excluir documento e seus chunks.
- Recusar embeddings de dimensão incompatível.
- Validar contratos dos handlers quando implementados.

Usar fixtures fictícias e banco exclusivo de testes; nunca apontar testes destrutivos
para produção. Marcar com `pytest.mark.integration` quando os testes existirem.
