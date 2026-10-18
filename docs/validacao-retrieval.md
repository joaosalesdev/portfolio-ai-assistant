# Validação inicial do retrieval

O objetivo é conferir os trechos recuperados e a resposta gerada. A geração
já está implementada, mas não há filtro mínimo de relevância. O contexto já é selecionado
com limite de tamanho e identificadores de fontes.
Os testes automatizados simulam OpenAI e PostgreSQL; a validação abaixo usa os
serviços reais e não foi executada pelo agente.

## Preparação

- Ativar a `.venv` e disponibilizar `OPENAI_API_KEY` e `DATABASE_URL` no processo.
- Confirmar que os documentos esperados já foram indexados com
  `text-embedding-3-small` e 1.536 dimensões.
- Usar preferencialmente uma credencial PostgreSQL de leitura para retrieval.
  A conexão do handler também solicita transações somente de leitura.

No DBeaver, conferir a distribuição dos chunks:

```sql
SELECT d.object_key, c.embedding_model, c.embedding_dimensions, count(*) AS chunks
FROM portfolio_documents d
JOIN portfolio_chunks c ON c.document_id = d.id
GROUP BY d.object_key, c.embedding_model, c.embedding_dimensions
ORDER BY d.object_key;
```

## Primeiro teste

Na raiz do projeto:

```bash
python scripts/invoke_retrieval.py
```

O script lê `tests/events/retrieval/post_question.json`. Essa execução chama a
OpenAI para embeddings e, quando há contexto, geração. Gera cobrança e consulta
o banco, sem atualizar os documentos.

No JSON de `body` da resposta, verificar:

- `statusCode` do envelope igual a 200.
- `matches_count` entre zero e cinco, dependendo da base.
- `matches` com texto, source, version_id, document_id, chunk_index e posições.
- `distance` em ordem crescente: menor distância significa vetor mais próximo.
- Evidência da resposta dentro do texto, não apenas um nome de arquivo adequado.

## Perguntas para career_goals.md

Altere a pergunta no campo `body` do evento, mantendo-o como uma string JSON.

| Pergunta | Evidência esperada |
| --- | --- |
| Quais oportunidades profissionais João Paulo procura e em quais regiões tem interesse em trabalhar? | Backend e Cloud Engineering; empresas de produto em Portugal e na Europa. |
| João quer participar de decisões arquiteturais? | Sistemas distribuídos, decisões arquiteturais e evolução como Software Engineer. |
| Quais princípios orientam as decisões de engenharia de João? | Simplicidade, problemas reais, desacoplamento, automação e aprendizado contínuo. |
| Em que tipo de vaga e país João gostaria de trabalhar? | Mesma evidência de oportunidades, apesar da mudança nas palavras. |
| Qual é a pretensão salarial de João? | O documento informa que esse dado não está disponível; não deve sustentar um valor salarial. |
| Qual é a receita de um bolo de chocolate? | Nenhuma evidência relevante; mesmo assim o Top-K pode retornar chunks. |

Repetir com perguntas de outros documentos já indexados. Com apenas um documento,
a busca quase sempre retornará esse documento, o que não comprova discriminação
semântica entre fontes. A falta de uma informação e a presença de um trecho dizendo
que ela não foi informada são situações diferentes.

## Como avaliar

Para cada pergunta, anotar a fonte e o trecho esperados antes de executar.
Registrar se a evidência aparece no primeiro resultado e entre os cinco primeiros.
Uma planilha simples com pergunta, esperado, encontrado e observação é suficiente.

Comparar paráfrases e perguntas sem resposta. Não interpretar a distância como
percentual de confiança ou garantia de verdade. Não escolher um threshold por
uma única pergunta; reunir exemplos positivos e negativos primeiro.

O padrão é Top-K 5. Para comparar 3 ou 10, alterar o argumento `top_k` da chamada
a `retrieve_chunks` no handler e repetir o mesmo conjunto de perguntas. A função
aceita valores de 1 a 20; o visitante não controla esse valor pelo JSON nesta etapa.

Se o resultado estiver ruim, verificar antes de mudar o modelo:

1. O documento correto e sua versão atual estão no banco?
2. Os trechos contêm a informação completa ou ela foi separada entre chunks?
3. Pergunta e documentos usam exatamente o mesmo modelo e dimensão?
4. O Top-K é suficiente para recuperar a evidência anotada?

## Erros e limites

- 400/405/413: revisar pergunta, método ou tamanho do corpo.
- 502: falha ao gerar embedding; conferir credencial, acesso à API e logs.
- 503: falha na consulta; conferir DATABASE_URL, acesso às tabelas, TLS e logs.
- 200 com `matches: []`: sem chunks compatíveis; isso não é erro técnico.

A consulta usa distância de cosseno e ordenação exata no esquema atual, sem índice
aproximado criado por esta etapa. Não cria tabelas nem grava dados. O handler
retorna trechos da base para inspeção, com resposta gerada no campo `answer`. Revisar a seleção
de conteúdo público antes de disponibilizar um endpoint. A Function URL e o CORS estão definidos no Terraform; aplicar e validar
conforme o guia de deployment antes de integrar o frontend.

## Conferir o contexto selecionado

Na resposta de `python scripts/invoke_retrieval.py`, comparar `matches` com
`sources` e `context`. Cada rótulo `[S1]`, `[S2]` etc. deve corresponder ao `id`
da fonte, com texto e metadados do chunk correto. Os identificadores são locais
a cada requisição, não IDs permanentes de documentos.

Verificar que `context` não ultrapassa 6.000 caracteres. Fontes vazias, duplicadas
ou grandes demais para o orçamento podem ser descartadas. `sources_count` pode
ser menor que `matches_count`; isso é esperado. `has_context: false` significa
que nenhum trecho foi selecionado, e `true` não comprova relevância para a pergunta.

Não há nova chamada paga ou consulta adicional na seleção: ela usa os resultados
já recuperados. O comando completo chama embeddings, PostgreSQL e geração quando há contexto.

## Conferir a geração

Executar `python scripts/invoke_retrieval.py` com as variáveis disponíveis. Verificar
`answer` e comparar cada afirmação com o trecho citado. O modelo esperado é
`gpt-6-luna`, com `generation_skipped: false` quando houver contexto. Sem contexto,
o modelo deve ser null e `generation_skipped: true`, com mensagem fixa de falta
de informação. Nenhuma chamada real foi feita pelo agente nesta implementação.

Testar uma pergunta respondível, uma paráfrase e uma sem informação documentada,
como pretensão salarial. Perguntas fora do assunto podem recuperar trechos mesmo
sem evidência suficiente; a resposta deve reconhecer a limitação.

A conferência automática de citações será implementada separadamente. Por enquanto,
verificar manualmente se cada `[S1]` etc. existe em `sources` e sustenta a afirmação.
HTTP 502 também pode indicar falha, saída incompleta ou vazia na geração.
