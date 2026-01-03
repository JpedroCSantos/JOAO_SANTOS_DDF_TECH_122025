# 🚀 Case Técnico Dadosfera: Modern Data Platform & AI

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Stack-Python_%7C_SQL-blue)
![Cloud](https://img.shields.io/badge/Cloud-AWS_%7C_Neon_%7C_Dadosfera-orange)

> **Autor:** João Pedro Santos
> **Processo:** Engenharia de Dados - Dadosfera
> **Período:** Dezembro/2025

---

## Objetivo do Projeto
Implementação ponta a ponta de uma Plataforma de Dados Moderna (Modern Data Stack) seguindo a arquitetura **Lakehouse**. O projeto simula um cenário real de engenharia de dados, cobrindo desde a ingestão de múltiplas fontes até a aplicação de Governança e Inteligência Artificial.

---
## Item 0 - Planejamento e Ingestão

**Gestão Ágil:** O acompanhamento das tarefas segue a metodologia Kanban.
📊 [**Acesse o Quadro do Projeto (Trello)**](https://trello.com/b/7aWCHtbz/dadosfera)

![Quadro Trello](/docs/images/trello_board.png)

### Estimativa de Esforço e Custos (Story Points)

Para cumprir o requisito de **Estimativa de Custos e Alocação de Recursos** (Item 0 - Avançado), este projeto adota o sistema de pontuação baseado na sequência de Fibonacci adaptada.

---

## Item 1 - Seleção e Arquitetura de Dados

### O Pivot: De E-commerce para PropTech
Originalmente planejado para Varejo (Olist), o projeto realizou um **Pivot Estratégico** para o setor de Turismo/Imobiliário.

* **Dataset:** [Inside Airbnb (Rio de Janeiro)](http://insideairbnb.com/get-the-data/)
* **Estratégia de Volumetria:**
    * O dataset original de *Reviews* possui escala de Big Data (milhões de registros).
    * **Decisão de Arquitetura:** Para este case, foi aplicada uma filtragem estratégica reduzindo a carga para **~300k linhas**.
    * **Objetivo:** Otimizar o tempo de processamento/custo da pipeline durante a fase de desenvolvimento, mantendo-se ainda **3x acima do requisito mínimo** do case (>100k registros).

* **Justificativa Técnica:** A base oferece maior complexidade para engenharia de dados por incluir nativamente:
    1.  **Dados Geoespaciais (GIS):** Polígonos de bairros (GeoJSON).
    2.  **Dados Desestruturados:** Reviews de usuários para análise de NLP.
    3.  **Dados Relacionais:** Tabelas de propriedades e calendário.

### Arquitetura "Hybrid-Cloud"
A solução integra serviços best-of-breed para compor o Data Lake:
* **Landing Zone:** AWS S3 (Armazenamento de arquivos brutos).
* **Transactional Layer:** Neon PostgreSQL (Simulação de banco de produção).
* **Platform Core:** Dadosfera (Ingestão, Catálogo e Processamento).

---
## Pipelines de Ingestão (Item 2.1)
Implementação de pipelines segregadas por domínio de dados (**Data Mesh**), garantindo que cada tipo de arquivo tenha seu fluxo de tratamento específico.

| Pipeline ID | Origem | Destino (Tabela) | Status | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **PL_INGEST_S3_AIRBNB_LISTINGS** | AWS S3 | `PUBLIC.LISTINGS` | ✅ | Dados cadastrais e financeiros (Core). |
| **PL_INGEST_S3_AIRBNB_REVIEWS** | AWS S3 | `PUBLIC.REVIEWS` | ✅ | Logs de avaliações (Alto Volume/Texto). |
| **PL_INGEST_S3_AIRBNB_GIS_ZONES** | AWS S3 | `PUBLIC.GIS_ZONES` | ✅ | Dados vetoriais de mapas (GeoJSON). |
| **PL_INGEST_NEON_REFERENCE_DATA**| Neon DB | `PUBLIC.NEIGHBOURHOODS` | ✅ | Replicação de dados mestres do Postgres. |

---

## Item 3 - Exploração e Governança (Data Lake)

Nesta etapa, focou-se na organização da **Landing Zone (Camada Bronze)** e na documentação dos ativos para garantir a democratização do acesso.

### 1. Estratégia de Catalogação
Os ativos foram classificados utilizando **Tags** na plataforma para identificar visualmente a camada e a função de cada tabela:

* **`Bronze`**: Aplicada a todas as tabelas de ingestão (`listings`, `reviews`, `gis_zones`), indicando que contêm dados brutos (Raw) e imutáveis da Landing Zone.
* **`Dimensão`**: Aplicada especificamente à tabela `NEIGHBOURHOODS` (origem Neon), identificando-a antecipadamente como uma tabela de referência (Master Data) para o modelo dimensional.

### 2. Dicionário de Dados
A documentação detalhada de cada coluna, tipagem e regras de negócio foi externalizada para manter este README limpo.

👉 **[Acesse o Dicionário de Dados Completo (Docs)](docs/data_dictionary.md)**

### 3. Matriz de Riscos e Decisões Técnicas (ADR)
Registro de impedimentos encontrados durante a ingestão e as soluções de contorno adotadas ("Workarounds").

| Decisão / Impedimento | Contexto Técnico | Solução Adotada (Trade-off) |
| :--- | :--- | :--- |
| **GeoJSON Aninhado (Nested Data)** | A ingestão do arquivo `neighbourhoods.geojson` resultou em uma única linha contendo um array JSON gigante, devido ao formato `FeatureCollection`. | **Decisão ELT:** Manter o dado aninhado na camada Bronze e realizar a explosão (`UNNEST`/`FLATTEN`) via SQL na etapa de transformação (Silver), preservando a fidelidade à fonte. |
| **Uso de Owner no Neon** | O usuário de serviço `dadosfera_user` falhou ao ler metadados do sistema (`pg_catalog`) na conexão JDBC. | **Decisão:** Uso temporário do superusuário `neondb_owner` para desbloquear o pipeline, documentado como Dívida Técnica de segurança. |


---

## Arquitetura de Processamento e Inteligência (Items 4, 5 & 6)

Para a execução das etapas de Qualidade de Dados, Enriquecimento com IA e Modelagem Dimensional, foi adotada uma arquitetura de **Computação Desacoplada (Decoupled Compute)**.

Esta decisão estratégica visa garantir a reprodutibilidade do ambiente científico e a agilidade no desenvolvimento, mantendo a compatibilidade total com a plataforma de destino (Dadosfera).

#### 1. Estratégia de Processamento (Hybrid ELT)
Devido a restrições de acesso ao módulo de computação nativo da plataforma SaaS durante a fase de avaliação, implementou-se o padrão **"Bring Your Own Compute" (BYOC)**:

1.  **Extract (Cloud):** Os dados brutos residem na Landing Zone (AWS S3/Dadosfera).
2.  **Transform & Quality (Local/Container):** O processamento pesado (Validação GX, NLP com GPT-4, Modelagem Star Schema) é executado em containers locais, simulando um *Worker Node* externo.
    * *Nota:* O código foi desenvolvido utilizando bibliotecas padrão (Python SDKs), permitindo um *Lift-and-Shift* imediato para dentro da Dadosfera ou Databricks sem refatoração.
3.  **Load (Cloud):** Os resultados processados (Camada Gold) são re-ingestados no Data Lake da Dadosfera para consumo via Dashboard.

#### 2. Abstração de I/O (Data Mocking)
Para otimizar custos e latência durante o ciclo de desenvolvimento, foi criada uma camada de abstração de leitura para os arquivos locais (`./data/raw/*.csv`) replicando a estrutura do S3.

## Item 4 - Data Quality & Saneamento (Great Expectations)

Para garantir a confiabilidade dos modelos de IA, implementou-se uma estratégia rigorosa de **Quality Gates** utilizando a biblioteca **Great Expectations (GX)**. O processo foi dividido em duas etapas: Diagnóstico (Raw) e Validação Final (Silver).

### Fase 1: Diagnóstico da Camada Bronze (Raw)
A primeira execução do GX sobre os dados brutos revelou problemas críticos que inviabilizariam o uso direto em Machine Learning:

* **Duplicidade:** 437 IDs de imóveis duplicados.
* **Integridade Numérica:** 3.789 registros com IDs "sujos" (erros de parser/cabeçalhos repetidos) nas tabelas de Reviews.
* **Regras de Negócio:** 4.398 imóveis com `price` nulo ou formatado incorretamente, o que quebraria cálculos financeiros.

> **Status Inicial:** ❌ FALHA (Expected)

---

## Item 4.1 (Bônus) - Transformação Silver & CDM

Para resolver os problemas detectados, foi desenvolvido o pipeline de transformação [`2_transform_silver.ipynb`](/nootbooks\02-transform_silver.ipynb). Além da limpeza, foi implementado um **Common Data Model (CDM)**, padronizando a nomenclatura das colunas para um padrão corporativo legível (Enterprise Naming Convention).

### 1. Ações de Saneamento
* **Cleaning:** Conversão forçada de tipagem (String -> Float/Int).
* **Filtering:** Remoção automática de linhas onde `ID` ou `Price` eram nulos/inválidos ("Garbage Collection").
* **Deduplication:** Aplicação de `drop_duplicates` baseada na Chave Primária.

### 2. Common Data Model (Schema Padrão)
Adoção de prefixos semânticos para facilitar o Self-Service BI:

| Prefixo | Significado | Exemplo Original | Exemplo CDM (Novo) |
| :--- | :--- | :--- | :--- |
| **SK_** | Surrogate/Source Key | `id` | `SK_LISTING` |
| **NM_** | Nome/Texto Curto | `neighbourhood` | `NM_BAIRRO` |
| **VLR_** | Valor Monetário | `price` | `VLR_DIARIA_BRL` |
| **NR_** | Número/Coordenada | `latitude` | `NR_LATITUDE` |
| **QTD_** | Quantidade/Métrica | `minimum_nights` | `QTD_MIN_NOITES` |

---

### Fase 3: Validação Final (Quality Gate)

Após a transformação, o Great Expectations foi re-executado sobre a camada **Bronze**. O resultado comprova a eficácia do pipeline de engenharia:

**Relatório de Execução (Silver Layer):**
```text
📊 RELATÓRIO: Listings (Silver)
Status Global: ✅ APROVADO
----------------------------------------
✅ [SK_LISTING] Unicidade Garantida
✅ [SK_LISTING] Não Nulo
✅ [VLR_DIARIA_BRL] Formato Numérico Validado
✅ [QTD_DIAS_DISPONIVEIS] Range Lógico (0-365) Validado

📊 RELATÓRIO: Reviews (Silver)
Status Global: ✅ APROVADO
----------------------------------------
✅ [SK_REVIEW] Formato Numérico Validado
✅ [SK_LISTING] Integridade Referencial (FK)
✅ [NM_REVIEWER] Preenchimento Obrigatório
```

## Item 5 - Enriquecimento com GenAI & LLMs (Feature Engineering)

Para extrair valor dos dados desestruturados (textos livres em Reviews e Títulos de Anúncios), foi implementado um pipeline de **Processamento de Linguagem Natural (NLP)** utilizando a API da OpenAI.

O objetivo não foi apenas "usar IA", mas sim transformar texto em colunas estruturadas para o Dashboard (Item 9), permitindo responder perguntas como: *"Qual o sentimento médio dos hóspedes?"* ou *"Imóveis com vista para o mar são mais caros?"*.

### Estratégia e FinOps (Amostragem Inteligente)
Devido ao volume de dados (300k+ registros), processar a base inteira seria ineficiente e custoso para uma Prova de Conceito (PoC). Adotou-se uma estratégia de **Smart Sampling** com foco em representatividade e economia:

1.  **Amostragem de Reviews (1.000 registros):**
    * **Top 500:** Reviews mais recentes/relevantes (Head).
    * **Random 500:** Seleção aleatória do restante da cauda (Tail) para evitar viés temporal.
2.  **Integridade Referencial de Listings:**
    * Seleção automática dos imóveis (`SK_LISTING`) citados nos reviews acima.
    * *Backfill* aleatório até completar 1.000 imóveis, garantindo massa de dados para análise cruzada.
3.  **Escolha do Modelo:**
    * **Modelo:** `gpt-4o-mini`.
    * **Custo Estimado da Operação:** < $0.10 USD (para processar os 2.000 registros).

### Engenharia de Prompt (As Missões da IA)

O pipeline executa duas "missões" distintas de classificação, forçando a saída em formato JSON (`response_format={"type": "json_object"}`) para garantir a integração direta com o Pandas.

#### Missão A: Análise de Sentimento (Tabela `fact_reviews`)
Transforma comentários subjetivos em métricas quantitativas.
* **Prompt:** *"Atue como um especialista em Customer Experience. Analise o review e retorne um JSON."*
* **Features Geradas:**
    * `SENTIMENTO`: Positivo, Neutro, Negativo.
    * `TOPICO_PRINCIPAL`: Limpeza, Localização, Ruído, Atendimento, etc.
    * `SUB_TOPICO`: Conforto, Comunicação, Valor, Comodidades, Outro.
    * `TOM_DE_URGENCIA`: Avaliação precisa de uma ação urgente.

#### Missão B: Categorização de Imóveis (Tabela `dim_listings`)
Extrai atributos de negócio a partir do título criativo do anúncio.
* **Prompt:** *"Atue como um Corretor de Imóveis Sênior. Analise o título do anúncio e classifique."*
* **Features Geradas:**
    * `CATEGORIA_VIBE`: Luxo, Econômico, Romântico, Familiar, Moderno.
    * `TIPO_VISTA`: Vista Mar, Urbana, Natureza, Sem Vista.
    * `PRINCIPAL_CARACTERISTICA`: Palavra única palavra que destaca o imóvel.
    * `PONTO_FORTE`: Resumo de 3 palavras (ex: "Perto do Metrô").

### Exemplo de Resultados (De/Para)

| Input (Texto Original) | Output (Enriquecido via LLM) |
| :--- | :--- |
| **Review:** *"O apartamento é lindo, mas o barulho da rua não deixou a gente dormir. A limpeza estava ok."* | `{ "sentimento": "Negativo", "topico": "Ruído", "sub_topico":Conforto, "tom_de_urgencia": false }` |
| **Listing:** *"COBERTURA DUPLEX VISTA MAR - COPACABANA POSTO 6"* | `{ "vibe": "Luxo", "vista": "Mar", "principal_caracteristica": "Localidade", "destaque": "Cobertura Duplex" }` |

### Persistência
Os dados enriquecidos foram salvos separadamente na camada Gold para consumo do Data App:
* `data/gold/sample_reviews_enriched.csv`
* `data/gold/sample_listings_enriched.csv`

## Item 6 - Modelagem de Dados (Data Warehouse)

Para a construção da camada **Gold** no Google BigQuery, adotou-se a metodologia **Dimensional (Kimball)**, criando um modelo **Star Schema** (Esquema Estrela).

Essa modelagem foi escolhida por ser otimizada para leitura em ferramentas de BI (Power BI/Streamlit) e facilitar consultas analíticas (OLAP), ao contrário do modelo normalizado (3NF) que prioriza a escrita (OLTP).

### Estrutura do Schema

O modelo é centrado no evento de avaliação ("Review"), cercado pelas dimensões de contexto:

#### 1. Fato: `FACT_REVIEWS`
Tabela transacional contendo métricas e chaves estrangeiras.
* **Granularidade:** 1 linha por avaliação única.
* **Métricas:** `TOM_DE_URGENCIA` (Boolean/Flag indicando críticas severas que exigem ação imediata).
* **Dimensão Degenerada:** `SENTIMENTO` (Positivo/Neutro/Negativo).

#### 2. Dimensão: `DIM_LISTINGS`
Contém os atributos descritivos do imóvel, enriquecidos com Features de IA.
* **Atributos:** `NM_ANUNCIO`, `VLR_DIARIA`, `CAT_VIBE_IA` (Luxo/Econômico...), `CAT_VISTA_IA` (Mar/Urbana...).
* **Slowly Changing Dimension (SCD):** Tratada como Tipo 1 (Sobrescreve valor atual) para simplificação do case.

#### 3. Dimensão: `DIM_NEIGHBOURHOODS` (GeoSpatial)
Tabela espacial oriunda do processamento do arquivo `neighbourhoods.geojson`.
* **Feature Especial:** Coluna do tipo `GEOGRAPHY` (Polígono) no BigQuery, permitindo queries espaciais (ex: `ST_CONTAINS`) para filtrar reviews dentro de zonas geográficas específicas no mapa.

#### 4. Dimensão: `DIM_TEMPO`
Calendário fiscal/civil para análises de sazonalidade.
* **Atributos:** Ano, Mês, Dia da Semana, Flag de Feriado, Flag de Alta Temporada.

---

### Diagrama de Entidade-Relacionamento (DER)

A figura abaixo representa a arquitetura física implementada:

![Diagrama de Mermaid](/docs/images/mermaid_diagram.png)