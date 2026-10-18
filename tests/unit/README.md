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

O `pytest.ini` configura os imports a partir de `src/`. Os 48 casos de parsing, ingestão, normalização, chunking, embeddings e persistência foram
validados localmente. O workflow de deploy agora executa `python -m pytest -v`
com Python 3.14 antes do build e da autenticação AWS. Alterações em `tests/`
ou `pytest.ini` também disparam o workflow em pushes na main. A execução desta
configuração no GitHub Actions ainda precisa ser confirmada após o push.

As pastas por módulo estão reservadas para os próximos comportamentos.
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
