# Infraestrutura — planejamento

Ainda não há recursos implantáveis nesta pasta.

| Artefato futuro | Responsabilidade | Campos a definir |
| --- | --- | --- |
| `Dockerfile.ingestion` | Imagem da indexação | runtime, dependências e handler implementado |
| `Dockerfile.query` | Imagem da consulta | runtime, dependências e handler implementado |
| Infraestrutura como código | Duas funções e permissões separadas | região, memória, timeout, concorrência |
| Function URL | Entrada da consulta | autenticação, CORS e proteção de consumo |
| Configuração de secrets | Referências externas | mecanismo de entrega e rotação |
| Banco local | PostgreSQL + pgvector | versão, volume e configuração local |

As imagens não devem incluir documentos locais ou credenciais. Escolheremos a
origem dos documentos de produção antes de implementar o handler de ingestão.
Este roteiro não é um Dockerfile, compose ou template de deploy funcional.
