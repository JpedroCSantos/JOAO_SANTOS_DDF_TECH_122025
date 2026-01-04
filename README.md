# 🚀 Case Técnico Dadosfera: Modern Data Platform & AI

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Stack-Python_%7C_SQL-blue)
![Cloud](https://img.shields.io/badge/Cloud-GCP_%7C_Neon_%7C_Dadosfera-orange)

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
* **Landing Zone:** Google Storage & AWS S3 (Armazenamento de arquivos brutos).
* **Transactional Layer:** Neon PostgreSQL (Simulação de banco de produção).
* **Platform Core:** Dadosfera (Ingestão, Catálogo e Processamento).

---
## Pipelines de Ingestão (Item 2.1)
Implementação de pipelines segregadas por domínio de dados (**Data Mesh**), garantindo que cada tipo de arquivo tenha seu fluxo de tratamento específico.

| Pipeline ID | Origem | Destino (Tabela) | Status | Descrição | Pipeline | Catalogo
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PL_INGEST_S3_AIRBNB_LISTINGS** | AWS S3 | [`PUBLIC.LISTINGS`] | ✅ | Dados cadastrais e financeiros (Core). | [Pipeline](https://app.dadosfera.ai/pt-BR/collect/pipelines/6caaa815-5faf-4888-9dd7-3da6451bd67f) | [Catálogo](https://app.dadosfera.ai/pt-BR/catalog/data-assets/f1028bb5-30fc-41af-b8dd-11171e50b3f1)
| **PL_INGEST_S3_AIRBNB_REVIEWS** | AWS S3 | `PUBLIC.REVIEWS` | ✅ | Logs de avaliações (Alto Volume/Texto). | [Pipeline](https://app.dadosfera.ai/pt-BR/collect/pipelines/ebdcae36-cb08-4670-ba26-98f8757d98aa) | [Catálogo](https://app.dadosfera.ai/pt-BR/catalog/data-assets/07faa045-ac65-4442-91f8-8069c853f744)
| **PL_INGEST_S3_AIRBNB_GIS_ZONES** | AWS S3 | `PUBLIC.GIS_ZONES` | ✅ | Dados vetoriais de mapas (GeoJSON). | [Pipeline](https://app.dadosfera.ai/pt-BR/collect/pipelines/bd5f8d0b-acab-4a59-8c8f-9e5a4a3f144b) | [Catálogo](https://app.dadosfera.ai/pt-BR/catalog/data-assets/d7c050a6-7668-4546-b16c-ab86b2d70edd)
| **PL_INGEST_NEON_REFERENCE_DATA**| Neon DB | `PUBLIC.NEIGHBOURHOODS` | ✅ | Replicação de dados mestres do Postgres. | [Pipeline](https://app.dadosfera.ai/pt-BR/collect/pipelines/6f4c5c79-1784-45a4-be64-34f91e29200b) | [Catálogo](https://app.dadosfera.ai/pt-BR/catalog/data-assets/f001ec60-15b0-4248-b381-eccd3ff72f67)
 
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


---

## Arquitetura de Processamento e Inteligência (Items 4, 5 & 6)

Para a execução das etapas de Qualidade de Dados, Enriquecimento com IA e Modelagem Dimensional, foi adotada uma arquitetura de **Computação Desacoplada (Decoupled Compute)**.

Esta decisão estratégica visa garantir a reprodutibilidade do ambiente científico e a agilidade no desenvolvimento, mantendo a compatibilidade total com a plataforma de destino (Dadosfera).

#### 1. Estratégia de Processamento (Hybrid ELT)
Devido a restrições de acesso ao módulo de computação nativo da plataforma durante a fase de avaliação, implementou-se o padrão **"Bring Your Own Compute" (BYOC)**:

1.  **Extract (Cloud):** Os dados brutos residem na Landing Zone (GCP/Dadosfera).
2.  **Transform & Quality (Local/Container):** O processamento pesado (Validação GX, NLP com GPT-4, Modelagem Star Schema) é executado em containers locais, simulando um *Worker Node* externo.
3.  **Load (Cloud):** Os resultados processados (Camada Gold) são re-ingestados no Data Lake da Dadosfera para consumo via Dashboard.

#### 2. Abstração de I/O (Data Mocking)
Para otimizar custos e latência durante o ciclo de desenvolvimento, foi criada uma camada de abstração de leitura para os arquivos locais (`./data/raw/*.csv`) replicando a estrutura do GCP & AWS S3.

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

Para resolver os problemas detectados, foi desenvolvido uma pipeline de transformação [`2_transform_silver.ipynb`](/nootbooks\02-transform_silver.ipynb). Além da limpeza, foi implementado um **Common Data Model (CDM)**, padronizando a nomenclatura das colunas para um padrão corporativo legível (Enterprise Naming Convention).

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

Após a transformação, o Great Expectations foi re-executado sobre os dados. O resultado comprova a eficácia da pipeline:

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

O objetivo não foi apenas "usar IA", mas sim transformar texto em colunas estruturadas para o Dashboard (Itens 7 e 9), permitindo responder perguntas como: *"Qual o sentimento médio dos hóspedes?"* ou *"Imóveis com vista para o mar são mais caros?"*.

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
* `data/gold/FACT_REVIEWS.csv`
* `data/gold/DIM_LISTINGS.csv`

## Item 6 - Modelagem de Dados (Data Warehouse)

Para a construção da camada **Gold**, adotou-se a metodologia **Dimensional (Kimball)**, criando um modelo **Star Schema** (Esquema Estrela).

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

---

## Item 7 - Análise de Dados e Insights de Negócio

Após a modelagem da camada Gold, foi realizada a etapa de **Análise de Dados**. O objetivo foi executar as consultas SQL desenvolvidas para responder às perguntas estratégicas do projeto e validar as hipóteses de negócio.

Utilizando a plataforma Dadosfera para visualização, consolidamos os dados de *Listings* (Imóveis) e *Reviews* (Avaliações Enriquecidas com IA) para gerar os seguintes insights:

### Visão Geral da Análise

![Overview da Análise Airbnb](/docs/images/dashboard_overview.jpg)
*(Figura: Painel consolidado com as respostas para as 5 perguntas de negócio)*

---

### Principais Descobertas (Data Storytelling)

Com base nas queries executadas na camada Gold, chegamos às seguintes conclusões:

#### 1. Precificação de Mercado (Baseline)
* **Pergunta:** Qual é o ticket médio das diárias no Rio de Janeiro?
* **Resultado:** **R$ 615,90**.
* **Análise:** Este valor serve como âncora para precificação. Imóveis muito abaixo disso podem indicar baixa qualidade ou oportunidade (dumping), enquanto valores muito acima precisam justificar o preço com atributos exclusivos (Vista Mar, Luxo).

#### 2. Perfil da Oferta (Hegemonia de Privacidade)
* **Pergunta:** Qual o tipo de acomodação predominante?
* **Resultado:** **83.2% são Casas/Apartamentos Inteiros**.
* **Análise:** O mercado do Rio é dominado por aluguéis de temporada completos. A oferta de "Quartos Privativos" (15.8%) e "Compartilhados" (1.0%) é minoritária, indicando que o público alvo busca privacidade total, competindo diretamente com a rede hoteleira.

#### 3. Reputação e Experiência (Via GenAI)
* **Pergunta:** Quais tópicos geram mais elogios ou críticas?
* **Resultado:** O tópico **"Localização"** é o maior ofensor positivo (barra verde predominante).
* **Análise:** A localização é o fator decisivo para a satisfação no Rio de Janeiro. Entretanto, pontos operacionais como **"Limpeza"** e **"Check-in"** aparecem com margem para melhoria, sendo onde os anfitriões perdem mais pontos.

#### 4. Comportamento de Reserva (Vibe vs. Estadia)
* **Pergunta:** Como o estilo do imóvel influencia a exigência de estadia mínima?
* **Resultado:** Imóveis classificados pela IA como **"Luxo"** ou **"Econômico"** exigem mais noites (média > 4).
* **Análise:**
    * *Luxo:* Foca em estadias longas para diluir custos operacionais altos.
    * *Relaxante/Romântico:* Aceitam estadias curtas (finais de semana), facilitando a conversão rápida.

#### 5. Distribuição Geográfica (Mancha de Calor)
* **Pergunta:** Onde se concentram os imóveis?
* **Resultado:** Alta densidade na Zona Sul (Orla) e Centro.
* **Análise:** O mapa de pontos confirma a saturação nos bairros turísticos clássicos (Copacabana, Ipanema). Existem vazios urbanos na Zona Norte que representam mercados inexplorados, porém com menor demanda turística natural.

### Queries SQL:

``` SQL
-- QUESTÃO 1: Qual é o valor médio da diária (Ticket Médio) de todos os imóveis cadastrados?
SELECT 
	AVG(VLR_DIARIA_BRL) 
FROM TB__OQ3K4Q__GOLD_LISTINGS_PL_INGEST_S3_AIRBNB

-- QUESTÃO 2: Qual a distribuição de imóveis por tipo de acomodação?
SELECT
    DS_TIPO_QUARTO AS TIPO_DE_QUARTO,
    COUNT(SK_LISTING) AS QTD_DE_IMOVEIS
FROM TB__OK6YZB__GOLD_LISTINGS_PL_INGEST_S3_AIRBNB_V2
GROUP BY 1
ORDER BY QTD_DE_IMOVEIS DESC;

-- QUESTÃO 3: Como os hóspedes estão avaliando cada aspecto (tópico) da experiência?
SELECT 
    CAT_TOPICO,
    CAT_SENTIMENTO,
    COUNT(SK_LISTING) AS QTD_REVIEWS
FROM TB__U5H8NM__GOLD_REVIEWS_PL_INGEST_S3_AIRBNB
GROUP BY CAT_TOPICO, CAT_SENTIMENTO
ORDER BY CAT_TOPICO, QTD_REVIEWS DESC;

-- QUESTÃO 4: Qual é a política de estadia mínima exigida para cada perfil de imóvel?
SELECT 
 CAT_VIBE_IA AS CATEGORIA,
 COUNT(SK_LISTING) AS QUANTIDADE_IMOVEIS,
 ROUND(AVG(QTD_MIN_NOITES),0) AS MEDIA_MIN_NOITES
FROM TB__OK6YZB__GOLD_LISTINGS_PL_INGEST_S3_AIRBNB_V2
GROUP BY CAT_VIBE_IA

-- QUESTÃO 5: Qual a localização exata de cada imóvel para plotagem no mapa?
SELECT 
    SK_LISTING AS ID_IMOVEL, 
    NR_LATITUDE AS LATITUDE, 
    NR_LONGITUDE AS LONGITUDE, 
FROM TB__OK6YZB__GOLD_LISTINGS_PL_INGEST_S3_AIRBNB_V2
```

## Item 8 - Pipelines e Orquestração

Embora a execução dos scripts tenha sido realizada nas etapas anteriores, este item documenta a orquestração lógica do fluxo de dados **(ELT/ETL)**. Devido a restrições de acesso ao módulo de *Transformação/Intelligence* da plataforma Dadosfera, optei por arquitetar o pipeline utilizando a stack nativa do **Google Cloud Platform (Vertex AI + BigQuery)**, demonstrando adaptabilidade e conhecimentos de Nuvem.

### Arquitetura do Pipeline

O pipeline foi desenhado para ser idempotente e sequencial, garantindo que os dados fluam da origem bruta até a camada analítica com qualidade e enriquecimento.

```mermaid
graph LR
    A[📂 CSV Locais] -->|Upload| B(☁️ Cloud Storage - Raw)
    B -->|Leitura| C{Vertex AI / Python}
    C -->|Validação| D[Great Expectations]
    C -->|Limpeza| E[Camada Silver]
    E -->|Enriquecimento| F[OpenAI API]
    F -->|Modelagem| G[BigQuery - Gold]
    G -->|Consumo| H[Dashboard]
```

### Detalhamento das Tasks

Abaixo, o fluxo de execução passo a passo (**Workflow**):

---

#### **Task 1: Ingestão (Data Ingestion)**

**Ação:**  
Upload dos arquivos brutos (`listings.csv`, `reviews.csv`) para o Bucket do **Google Cloud Storage** e **AWS S3**.

**Script:**  
- Upload via Console

**Objetivo:**  
Centralizar os dados na **Landing Zone (Raw)**, garantindo backup e disponibilidade para o ambiente de processamento.

---

#### **Task 2: Saneamento (Silver Layer)**

**Ação:**  
Leitura dos dados do Bucket e aplicação de regras de limpeza via **Pandas**.

**Transformações:**
- Remoção de colunas desnecessárias (PII ou irrelevantes para análise) para otimizar storage  
- Tratamento de valores nulos e conversão de tipos (ex: `String → Float` em colunas de preço)

**Data Quality:**  
Execução da suite de testes do **Great Expectations** (ver Item 7).

---

#### **Task 3: Enriquecimento com IA (Feature Engineering)**

**Ação:**  
Criação de colunas calculadas semânticas que não existiam na base original.

**Processo:**
- Envio de micro-lotes de textos (Reviews / Títulos) para a **API da OpenAI**

**Output:**  
Geração das colunas:
- `CAT_SENTIMENTO`
- `CAT_VIBE`
- `FLG_URGENCIA`

**Impacto:**  
Transformação de dados não estruturados em dados tabulares prontos para consumo via SQL.

---

#### **Task 4: Modelagem e Carga (Gold Layer)**

**Ação:**  
Aplicação das regras de negócio finais e persistência no **Data Warehouse**.

**Transformações:**
- Renomeação de colunas para o padrão **CDM (Common Data Model)**
- Tradução de domínios (ex: `Entire home → Casa Inteira`)

**Carga:**  
Escrita no **BigQuery** utilizando a biblioteca `pandas-gbq`.

---

### Decisões de Arquitetura

#### **1. Por que Pandas e não Apache Spark?**

Uma decisão consciente de **FinOps (Engenharia de Custos)** foi tomada neste projeto.

**Volume de Dados:**  
O dataset do Airbnb Rio de Janeiro possui cerca de **300k a 500k registros** (*Small Data*).

**Justificativa:**  
O Pandas processa esse volume **em memória (In-Memory)** em poucos segundos, utilizando uma máquina **e2-standard-4** de baixo custo.

**Trade-off:**  
A utilização de um cluster Spark (Dataproc) traria:
- Overhead de tempo de start-up  
- Custo financeiro desnecessário para essa volumetria  

O **Apache Spark** seria a escolha correta apenas se o volume escalasse para **Gigabytes ou Terabytes**.

---

#### **2. Adaptação à Plataforma**

Como não foi possível utilizar o pipeline visual da **Dadosfera** (limitação de acesso), a mesma lógica de transformação foi replicada utilizando o **Vertex AI Workbench**.

## Item 9 & Bonus - Data App & Soluções de GenAI

Para consolidar toda a inteligência gerada nas camadas anteriores, foi desenvolvido um **Data App** interativo (construído em Streamlit). Esta aplicação não serve apenas para visualizar dados passados, mas atua como uma ferramenta prescritiva e generativa para dois perfis de usuário: o **Anfitrião (Host)** e o **Investidor**.

O aplicativo foi dividido em três módulos estratégicos:

### Módulo 1: Market Intelligence (Dashboard)
*Foco: Visualização e Diagnóstico de Mercado.*

Este módulo exibe os indicadores calculados na Camada Gold, permitindo uma visão macro e micro do turismo no Rio de Janeiro.
* **Mapa de Calor:** Identificação de zonas de alta densidade de ofertas.
* **Filtros Dinâmicos:** Segmentação por Bairro, Faixa de Preço e "Vibe" (Classificação da IA).
* **Análise de Sentimento:** Gráficos que mostram o que os hóspedes estão elogiando ou criticando em tempo real.

---

### Módulo 2: O "Gerador de Anúncios Perfeitos" (GenAI)
*Foco: Ferramenta para Anfitriões (Hosts).*

Utilizando a API da OpenAI integrada ao Streamlit, criamos um assistente que resolve a "dor" de criar um anúncio atrativo e precificá-lo corretamente.

#### Como funciona:
1.  **Input do Usuário:** O host seleciona as características do imóvel via *checkboxes* (ex: "Vista Mar", "Wi-Fi Rápido", "Perto do Metrô") e define o bairro.
2.  **Motor de Precificação (Analytics):** O app consulta a base Gold, filtra imóveis similares no mesmo bairro e calcula a mediana de preço (`VLR_DIARIA_BRL`), sugerindo um valor competitivo.
3.  **Motor Criativo (LLM):** Um prompt engenheirado recebe as características e gera uma descrição persuasiva (Copywriting) baseada nas melhores práticas de SEO do Airbnb.

> **Exemplo de Saída:**
> * *"Preço Sugerido: R$ 450,00/noite (5% abaixo da média da região para atrair os primeiros hóspedes)."*
> * *"Descrição Gerada: Acorde com a brisa do mar neste apartamento exclusivo..."*

---

### Módulo 3: O "Smart Investor" (Recomendação)
*Foco: Ferramenta para Investidores Imobiliários.*

Este módulo utiliza dados históricos para encontrar oportunidades de investimento (Arbitragem), cruzando o orçamento do usuário com a liquidez da região.

#### Lógica de Recomendação:
1.  **Input:** O usuário informa quanto deseja pagar na parcela do financiamento (ex: R$ 3.000/mês).
2.  **Cálculo de Viabilidade:** O sistema estima a receita potencial (Diária Média x Taxa de Ocupação Estimada via volume de Reviews).
3.  **Análise de "Blue Ocean":**
    * O algoritmo identifica bairros com **Alta Demanda** (Muitos reviews recentes).
    * Verifica a **Saturação de Oferta** (Ex: O bairro tem muita procura por "Luxo", mas 90% dos anúncios são "Econômicos"?).
4.  **Sugestão:** O app recomenda onde comprar e qual perfil de imóvel montar.

> **Cenário de Exemplo:**
> *"Com uma parcela de R$ 3.000, sugerimos investir no bairro **Botafogo**. A região possui alta liquidez (ocupação constante). Notamos uma escassez de imóveis com perfil **'Home Office/Nomad'** (Internet rápida + Mesa), apesar da alta procura por este perfil na área."*

---

### Stack Tecnológica do App
* **Frontend:** Streamlit (Python).
* **Backend de Dados:** Google BigQuery (Consultas SQL otimizadas).
* **Inteligência Artificial:** OpenAI API (`gpt-4o-mini`) para geração de texto e classificação.
* **Geospatial:** Plotly/Folium para renderização de mapas interativos.