# Fontes da base de conhecimento

Esta pasta guarda o conteúdo selecionado para o RAG. Os modelos são placeholders,
não fatos profissionais. Nenhum está aprovado para indexação.

```text
knowledge/
    manifest.yaml
    documents/     # Conteúdo público revisado e modelos de preenchimento
    raw/           # Originais locais ainda não revisados; ignorado pelo Git
    private/       # Nunca indexado; ignorado pelo Git
```

`raw/` e `private/` possuem instruções locais de exemplo nesta cópia de trabalho,
mas não serão versionados nem aparecerão em novos clones. Prefira guardar material
confidencial fora do projeto.

Os modelos específicos de cada projeto já foram criados. Consulte o
[inventário completo](../docs/examples.md) antes de preencher os documentos.

## Como adicionar um documento

1. Prepare e revise o texto fora dos arquivos versionados se ainda contiver
   informações privadas. Não coloque secrets ou documentos confidenciais no Git.
2. Use um modelo de `documents/` para produzir um Markdown público, por exemplo
   `documents/melita.md`. Preencha somente fatos verificáveis e remova placeholders.
3. Adicione uma entrada em `manifest.yaml` com `source_key` único e estável,
   título, projeto e caminho relativo a `knowledge/`.
4. Mantenha `approved_for_publication: false` até concluir a revisão do conteúdo.
   Depois altere para `true` para autorizar o futuro pipeline a processá-lo.
5. Revise o diff antes de fazer commit. A flag controla elegibilidade para
   indexação; **não esconde o arquivo de um repositório público**.

O manifesto é um contrato inicial: seu parser e o loader ainda não existem.
O futuro loader deverá aceitar apenas arquivos Markdown explicitamente aprovados
dentro de `documents/`, rejeitando caminhos externos e sem varrer outras pastas.
Entradas desabilitadas devem ser ignoradas, inclusive as dos modelos.

## Diferença para docs/

- `knowledge/`: fontes profissionais que poderão fundamentar as respostas.
- `docs/`: documentação de engenharia do próprio assistente, como decisões,
  experimentos e procedimentos de operação.

`docs/` não será indexada automaticamente. Se algum conteúdo de engenharia for
útil ao chatbot, selecione uma versão pública em `documents/` e registre sua
origem e aprovação no manifesto.
