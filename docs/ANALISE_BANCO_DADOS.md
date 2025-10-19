# Análise do Banco de Dados - Gestão Inteligente de Vagas (GIV)

## 📋 Resumo Executivo

Este documento apresenta uma análise completa das tabelas do banco de dados utilizadas no sistema **Gestão Inteligente de Vagas - GIV**. O sistema utiliza arquivos Parquet organizados na pasta `db/` para armazenar dados de solicitações médicas e procedimentos.

---

## 🗂️ Estrutura de Dados

### Localização dos Arquivos
- **Diretório**: `db/`
- **Formato**: Arquivos Parquet (Apache Parquet)
- **Total de arquivos**: 147 arquivos
- **Organização**: Particionamento por tipo de tabela

---

## 📊 Tabelas Principais Utilizadas

### 1. Tabela `solicitacao` (Principal)

**Arquivos**: `db/solicitacao-*.parquet`
- **Quantidade**: 40 arquivos particionados
- **Total de registros**: 3.210.746 registros
- **Finalidade**: Armazena dados das solicitações médicas dos pacientes

#### Estrutura de Colunas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `solicitacao_id` | String | ID único da solicitação |
| `paciente_id` | String | Identificador do paciente |
| `paciente_sexo` | String | Sexo do paciente |
| `paciente_faixa_etaria` | String | Faixa etária do paciente |
| `solicitacao_status` | String | Status atual da solicitação |
| `solicitacao_risco` | String | Nível de risco (VERMELHO, AMARELO, VERDE, AZUL) |
| `procedimento_sisreg_id` | String | ID do procedimento (chave estrangeira) |
| `data_solicitacao` | DateTime | Data da solicitação |
| `data_desejada` | DateTime | Data desejada pelo paciente |
| `data_cancelamento` | DateTime | Data de cancelamento (se aplicável) |
| `data_atualizacao` | DateTime | Data da última atualização |
| `solicitacao_situacao` | String | Situação da solicitação |
| `solicitacao_visualizada_regulador` | Boolean | Se foi visualizada pelo regulador |
| `cid_id` | String | Código CID da doença |
| `central_solicitante` | String | Central que fez a solicitação |
| `central_reguladora` | String | Central reguladora responsável |
| `unidade_solicitante_id_cnes` | String | CNES da unidade solicitante |
| `unidade_desejada_id_cnes` | String | CNES da unidade desejada |
| `profissional_solicitante_id` | String | ID do profissional solicitante |
| `operador_solicitante_id` | String | ID do operador solicitante |
| `operador_cancelamento_id` | String | ID do operador que cancelou |
| `vaga_solicitada_tp` | String | Tipo de vaga solicitada |
| `laudo_descricao_tp` | String | Tipo de descrição do laudo |
| `laudo_situacao` | String | Situação do laudo |
| `laudo_data_observacao` | DateTime | Data de observação do laudo |

### 2. Tabela `procedimento` (Secundária)

**Arquivos**: `db/procedimento-*.parquet`
- **Quantidade**: 1 arquivo
- **Total de registros**: 806 registros
- **Finalidade**: Catálogo de procedimentos médicos disponíveis

#### Estrutura de Colunas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `procedimento_sisreg_id` | String | ID único do procedimento (chave primária) |
| `procedimento` | String | Nome descritivo do procedimento |
| `procedimento_tipo` | String | Tipo do procedimento (ex: CIRURGIA) |
| `procedimento_especialidade` | String | Especialidade médica |
| `vagas_esperadas_hora` | Float | Número de vagas esperadas por hora |
| `proporcao_esperada_primeira_vez` | Float | Proporção esperada para primeira vez |
| `proporcao_esperada_retorno` | Float | Proporção esperada para retorno |

---

## 🔗 Relacionamentos

### Chave de Relacionamento
- **Campo**: `procedimento_sisreg_id`
- **Tipo de JOIN**: LEFT JOIN
- **Finalidade**: Enriquecer dados das solicitações com informações detalhadas dos procedimentos

### Fluxo de Dados
```
solicitacao (3.210.746 registros)
    ↓ (procedimento_sisreg_id)
procedimento (806 registros)
    ↓
Dataset Enriquecido (para análise)
```

---

## 📈 Análise de Volume de Dados

### Distribuição por Arquivos
- **Solicitações**: 40 arquivos particionados
- **Procedimentos**: 1 arquivo consolidado
- **Média de registros por arquivo de solicitação**: ~80.268 registros

### Crescimento de Dados
- **Total de solicitações**: 3.2 milhões de registros
- **Catálogo de procedimentos**: 806 procedimentos únicos
- **Relacionamento**: Muitos-para-um (muitas solicitações para um procedimento)

---

## 🎯 Utilização no Dashboard

### Funcionalidades Implementadas
1. **Filtros por Risco**: Utiliza campo `solicitacao_risco`
2. **Filtros por Especialidade**: Utiliza campo `procedimento_especialidade`
3. **Análise de Status**: Utiliza campo `solicitacao_status`
4. **Análise Demográfica**: Utiliza campos `paciente_faixa_etaria` e `paciente_sexo`
5. **Machine Learning**: Utiliza múltiplos campos para predição de agravamentos

### KPIs Calculados
- **Taxa de Confirmação**: Baseado em `solicitacao_status`
- **Risco Crítico**: Baseado em `solicitacao_risco`
- **Pacientes sem Agendamento**: Baseado em `solicitacao_status`
- **Distribuição por Especialidade**: Baseado em `procedimento_especialidade`

---

## 📁 Tabelas Disponíveis (Não Utilizadas)

O sistema possui outras tabelas que **não são utilizadas** pelo dashboard atual:

### Tabelas de Histórico
- `equipamento_historico-*.parquet` - Histórico de equipamentos
- `habilitacao_historico-*.parquet` - Histórico de habilitações
- `leito_historico-*.parquet` - Histórico de leitos
- `profissional_historico-*.parquet` - Histórico de profissionais (18 arquivos)
- `unidade_historico-*.parquet` - Histórico de unidades

### Tabelas Operacionais
- `marcacao-*.parquet` - Marcações de consultas (57 arquivos)
- `oferta_programada-*.parquet` - Ofertas programadas (24 arquivos)
- `tempo_espera-*.parquet` - Tempos de espera

### Tabelas de Referência
- `cids-*.parquet` - Códigos CID de doenças

---

## 🔧 Tecnologia Utilizada

### Processamento de Dados
- **Biblioteca**: Polars (Python)
- **Formato**: Apache Parquet
- **Vantagens**: 
  - Compressão eficiente
  - Leitura rápida
  - Suporte a tipos complexos
  - Particionamento automático

### Carregamento de Dados
```python
# Carregamento das solicitações
solicitacao_files = glob.glob("db/solicitacao-*.parquet")
df_solicitacao = pl.concat([pl.read_parquet(f) for f in solicitacao_files])

# Carregamento dos procedimentos
procedimento_files = glob.glob("db/procedimento-*.parquet")
df_procedimento = pl.concat([pl.read_parquet(f) for f in procedimento_files])

# JOIN entre as tabelas
df_completo = df_solicitacao.join(
    df_procedimento, 
    on="procedimento_sisreg_id", 
    how="left"
)
```

---

## 📊 Métricas de Performance

### Tempo de Carregamento
- **Cache implementado**: Dados são carregados uma vez e mantidos em memória
- **Otimização**: Uso de Polars para processamento eficiente
- **Particionamento**: Arquivos divididos para facilitar carregamento paralelo

### Uso de Memória
- **3.2M registros**: Estimativa de ~500MB a 1GB em memória
- **Cache global**: Evita recarregamento desnecessário
- **Limitação de registros**: Máximo de 5.000 registros por tabela na interface

---

## 🚀 Recomendações

### Otimizações Sugeridas
1. **Índices**: Considerar criação de índices nos campos mais consultados
2. **Particionamento**: Otimizar particionamento por data ou região
3. **Compressão**: Avaliar diferentes algoritmos de compressão
4. **Cache distribuído**: Para ambientes com múltiplas instâncias

### Expansão de Funcionalidades
1. **Integração com outras tabelas**: Utilizar tabelas de histórico para análises temporais
2. **Análise de tempo de espera**: Integrar dados de `tempo_espera`
3. **Análise de marcações**: Utilizar dados de `marcacao` para análise de agendamentos
4. **Análise de ofertas**: Integrar `oferta_programada` para análise de capacidade

---

## 📝 Conclusão

O sistema **Gestão Inteligente de Vagas - GIV** utiliza uma arquitetura de dados eficiente baseada em arquivos Parquet, com foco principal em duas tabelas:

1. **`solicitacao`**: Tabela principal com dados dos pacientes e solicitações
2. **`procedimento`**: Tabela de referência com informações dos procedimentos

A estrutura atual suporta eficientemente as funcionalidades do dashboard, com capacidade para análise de milhões de registros em tempo real. O sistema possui potencial para expansão utilizando as outras tabelas disponíveis no banco de dados.

---

**Documento gerado em**: $(date)  
**Versão do sistema**: 2.0.0  
**Total de registros analisados**: 3.211.552 registros


