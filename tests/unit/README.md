# Testes unitários

Os testes usam pytest, funções simples e `assert`, sem chamadas à AWS ou APIs pagas.

## Cobertura atual

`test_s3_event.py` contém cinco testes:

- Interpretação do evento real e identificação do objeto.
- Múltiplos registros, chave codificada e ausência dos campos opcionais.
- Rejeição de evento sem `Records`.
- Rejeição de evento de exclusão, não suportado no fluxo atual.
- Rejeição de registro sem a chave do objeto.

A fixture carrega `tests/events/indexing/s3_object_created.json`, que reproduz
um evento real fornecido pelo mantenedor. Ela é recarregada para cada teste.

## Execução

Na raiz do projeto, com o ambiente virtual ativado:

```bash
python -m pip install 'pytest>=8.3,<10'
python -m pytest -v
```

Para executar somente os testes da entrada S3:

```bash
python -m pytest tests/unit/test_s3_event.py -v
```

O `pytest.ini` configura os imports a partir de `src/`. Em 23/10/2026, os 77 casos de parsing, ingestão, normalização, chunking, embeddings,
persistência, retrieval e geração passaram localmente com clientes simulados. O workflow de deploy agora executa `python -m pytest -v`
com Python 3.14 antes do build e da autenticação AWS. Alterações em `tests/`
ou `pytest.ini` também disparam o workflow em pushes na main. O deploy e a operação do assistente integrado ao portfólio já foram confirmados
pelo mantenedor. Essa confirmação não transforma a suíte em testes de integração
com AWS, OpenAI ou PostgreSQL reais.

Os testes estão organizados por responsabilidade da aplicação.
Os JSONs em `tests/events/` são fixtures, não testes executáveis por si só.

## Ingestão

`ingestion/test_loader.py` verifica leitura com e sem versão, preservação do texto
UTF-8 e metadados, fechamento do corpo da resposta, rejeição de formato e conteúdo
inválidos, integração do handler com múltiplos documentos e propagação de falha S3.
O cliente S3 é simulado com `unittest.mock`, disponível no Python; os testes são pytest.

```bash
python -m pytest tests/unit/ingestion/test_loader.py -v
```

## Normalização

`ingestion/test_preprocessor.py` contém quatro testes para normalização de
quebras de linha e espaços, preservação de Markdown e código e idempotência
(processar o texto duas vezes mantém o mesmo resultado). O teste do handler
confere que o preprocessor é chamado para cada documento.

```bash
python -m pytest tests/unit/ingestion/test_preprocessor.py -v
```

## Chunking

`ingestion/test_chunker.py` contém cinco testes: documento curto com metadados,
preferência por parágrafos, divisão de parágrafos longos sem perda de texto e com
posições corretas, texto vazio e limite inválido. O teste do handler também verifica
que o chunker é chamado para cada documento e que a contagem é retornada.

```bash
python -m pytest tests/unit/ingestion/test_chunker.py -v
```

## Embeddings

`embeddings/test_embedding_service.py` usa um cliente OpenAI simulado para verificar
metadados, ordenação dos vetores, divisão em lotes, entrada vazia, respostas inválidas
e propagação de falhas. O teste do handler simula a etapa de embeddings.
Nenhuma chave ou chamada paga é necessária para executar pytest.

```bash
python -m pytest tests/unit/embeddings/test_embedding_service.py -v
```

## Persistência

`persistence/test_vector_repository.py` verifica a sequência de escrita na
transação, o bloqueio do registro, a rejeição de origem incorreta, o descarte de
eventos repetidos/antigos e a propagação de falhas ao contexto transacional.
A conexão é simulada; esses testes não substituem uma validação no PostgreSQL
real do SQL, rollback e concorrência.

```bash
python -m pytest tests/unit/persistence/test_vector_repository.py -v
```

## Entrada de retrieval

`retrieval/test_question.py` testa pergunta válida, body base64, JSON e perguntas
inválidos, limite de caracteres, método não suportado, evento malformado e limite
do corpo. O script local usa `tests/events/retrieval/post_question.json`.

```bash
python -m pytest tests/unit/retrieval/test_question.py -v
```

## Normalização da pergunta

`retrieval/test_query_preprocessor.py` contém três testes para normalização de
espaços e quebras de linha, preservação de acentos/maiúsculas/pontuação e
idempotência. O teste de pergunta válida do handler também verifica a integração.
Não há chamadas externas nem dependências adicionais.

```bash
python -m pytest tests/unit/retrieval/test_query_preprocessor.py -v
```

## Embedding da pergunta

O serviço de embeddings testa a configuração compartilhada com os documentos e
a rejeição de pergunta vazia antes de chamar a API. Os testes do handler usam uma
factory OpenAI simulada, verificam o envio da pergunta normalizada e o retorno
HTTP 502 sem detalhes internos quando a geração falha. Entradas inválidas não
criam o cliente OpenAI. A suíte não faz chamadas pagas.

## Busca vetorial

`retrieval/test_retriever.py` verifica a consulta parametrizada por cosseno, os
filtros de modelo/dimensão, Top-K, resultados vazios e rejeição de vetores inválidos.
Os testes do handler simulam PostgreSQL, verificam o retorno dos matches e o erro
HTTP 503 sem detalhes internos. Os 77 casos da suíte passam sem serviços externos.

```bash
python -m pytest tests/unit/retrieval -v
```

A relevância semântica e a execução SQL real precisam de validação separada:
[guia de validação](../../docs/validacao-retrieval.md).

## Seleção de contexto

`retrieval/test_context_selector.py` contém cinco testes: ordem e metadados das
fontes, orçamento com rótulos/separadores, descarte de chunks grandes sem corte,
textos vazios/duplicados e limite inválido. Os testes do handler conferem contexto
vazio e associação entre o identificador S1 e a fonte retornada.

```bash
python -m pytest tests/unit/retrieval/test_context_selector.py -v
```

## Geração de respostas

`generation/test_generator.py` verifica pergunta e contexto separados das instruções,
modelo e parâmetros, ausência de chamada sem contexto, saída vazia/incompleta e
propagação de falhas. Os testes do handler verificam a resposta e HTTP 502 em
falhas. Os 77 testes usam clientes simulados e não fazem chamadas pagas.

```bash
python -m pytest tests/unit/generation -v
```

A validação automática das citações ainda não faz parte desta implementação.

## O que ainda validar em produção

O chat já está funcionando, conforme confirmação do mantenedor. Continuar avaliando
relevância dos trechos, sustentação das respostas, perguntas sem informação,
atualização da base e erros. Registrar perguntas e evidências esperadas permite
comparar resultados ao alterar conteúdo, chunking, Top-K ou instruções.

A suíte simulada não comprova resistência a prompt injection, qualidade factual,
rollback real nem comportamento sob concorrência. Exclusões S3 e conferência
automática das citações ainda não estão implementadas. Testes reais de consulta
podem consumir a API; a invocação real de indexing também grava no banco.

## Notificações Telegram

`notifications/test_telegram.py` simula o transporte HTTP e cobre envio da pergunta
com resposta, configuração ausente, divisão de mensagens Unicode, rejeição da API
e falha sem expor o token. O handler testa que a notificação recebe a resposta e
que falhas ou pouco tempo restante não interrompem o chat.

```bash
python -m pytest tests/unit/notifications tests/unit/retrieval/test_question.py -v
```

A suíte contém 77 casos; nenhuma mensagem real é enviada. Os testes Terraform
verificam credenciais opcionais somente no retrieval e rejeição de configuração
incompleta. App contém nove testes simulados e base contém um.
