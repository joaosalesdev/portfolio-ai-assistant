# Testes unitários

Ainda não há testes nesta nova estrutura. Serão criados junto com cada comportamento
implementado, começando pelo loader. Usar documentos fictícios e clientes substitutos,
sem AWS ou chamadas pagas. `pytest.ini` configura os imports a partir de `src/`.

As pastas ingestion/, embeddings/, retrieval/, generation/ e persistence/ espelham
os módulos da aplicação. Arquivos .gitkeep apenas preservam as pastas no Git.
Os exemplos de eventos externos estão em ../events/ e não executam testes sozinhos.
