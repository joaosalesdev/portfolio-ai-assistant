# Testes unitários

Os testes usam pytest, funções simples e `assert`, sem chamadas à AWS ou APIs pagas.

## Cobertura atual

`test_s3_event.py` contém cinco testes:

- Interpretação do evento real e retorno do handler com os dados do objeto.
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

O `pytest.ini` configura os imports a partir de `src/`. Os cinco testes foram
validados localmente. Eles ainda não fazem parte do workflow de deploy.

As pastas por módulo estão reservadas para os próximos comportamentos.
Os JSONs em `tests/events/` são fixtures, não testes executáveis por si só.
