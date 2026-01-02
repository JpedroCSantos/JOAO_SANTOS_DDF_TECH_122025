# Dicionário de Dados: Case Airbnb Rio de Janeiro (Bronze)

Este documento detalha os ativos de dados ingeridos na *Landing Zone* (Camada Raw) do Data Lake.

---

## Tabela: PUBLIC.LISTINGS (Imóveis)
**Domínio:** Property System (Core)
**Origem:** S3 Bucket (`/property_system/listings.csv`)
**Frequência de Carga:** Diária (Batch)

### Descrição do Negócio
Base cadastral contendo o inventário de propriedades ativas. Este dataset é a fonte da verdade para características físicas dos imóveis, regras de locação e precificação base.

### Estrutura de Colunas (Schema)

| Coluna | Classificação | Descrição Funcional |
| :--- | :--- | :--- |
| **id** | `PK` | Identificador único da propriedade. Chave primária do sistema Airbnb. |
| **name** | `Descritivo` | Título do anúncio conforme exibido na plataforma. |
| **host_id** | `FK` | Identificador único do anfitrião (Host). Relaciona-se com a dimensão de usuários. |
| **neighbourhood_cleansed**| `FK` | Nome normalizado do bairro. Chave de ligação com a base geoespacial (`neighbourhoods`). |
| **room_type** | `Categoria` | Tipo de acomodação (Ex: 'Entire home/apt', 'Private room'). |
| **price** | `Métrica` | Valor da diária na moeda local (BRL). **Atenção:** Campo bruto contendo símbolos ('$') que requerem limpeza. |
| **minimum_nights** | `Regra` | Quantidade mínima de noites exigida para reserva. |
| **availability_365** | `Métrica` | Dias disponíveis para reserva na janela futura de 365 dias. Indicador de ociosidade. |

---

## Tabela: PUBLIC.REVIEWS (Avaliações)
**Domínio:** Customer Experience
**Origem:** S3 Bucket (`/customer_experience/reviews.csv`)
**Classificação:** ⚠️ Contém PII (Dados Pessoais)

### Descrição do Negócio
Log histórico de feedbacks deixados por hóspedes após o checkout. Dataset de alto volume utilizado para monitoramento de qualidade e análise de sentimento.

### Estrutura de Colunas (Schema)

| Coluna | Classificação | Descrição Funcional |
| :--- | :--- | :--- |
| **ID** | `PK` | Identificador único do registro da avaliação. |
| **DATE** | `Temporal` | Data de publicação do comentário (YYYY-MM-DD). Base para análise de sazonalidade. |
| **LISTING_ID** | `FK` | Identificador do imóvel avaliado. Conecta o feedback à propriedade. |
| **REVIEWER_ID** | `FK` | Identificador único do hóspede avaliador. |
| **REVIEWER_NAME** | `PII` | Nome público do avaliador. **Dado Sensível (LGPD):** Requer anonimização em camadas analíticas. |
| **COMMENTS** | `Unstructured`| Texto livre com a opinião do hóspede. Insumo para processamento de linguagem natural (NLP). |

---

## Tabela: PUBLIC.GIS_ZONES (Geoespacial)
**Domínio:** Intelligence / GIS
**Origem:** S3 Bucket (`/gis_data/neighbourhoods.geojson`)
**Formato:** GeoJSON / WKT
**Status:** ⚠️ Raw / Nested Data (Dados Aninhados)
**Formato Original:** GeoJSON FeatureCollection
**Estratégia de Processamento:** ELT (Extract-Load-Transform)

### Contexto Técnico
Esta tabela representa a ingestão bruta do arquivo `neighbourhoods.geojson`. Devido à estrutura hierárquica do formato GeoJSON, a plataforma carregou o objeto raiz (`FeatureCollection`) como um único registro.

**Atenção para Analistas:**
Os dados úteis não estão acessíveis diretamente. Eles encontram-se encapsulados no array JSON da coluna `features`.

### Estrutura de Colunas (Atual)

| Coluna | Tipo | Descrição Técnica & Ação Necessária |
| :--- | :--- | :--- |
| **type** | String | Metadado do formato (Valor fixo: "FeatureCollection"). |
| **features** | **JSON/Array** | **Coluna Principal.** Contém um array de objetos onde cada elemento representa um bairro (Polígono + Nome). <br> **Ação Futura:** Requer aplicação de função `UNNEST` ou `LATERAL FLATTEN` em SQL para normalizar em linhas individuais. |
| **_processing_timestamp** | Timestamp | Data/Hora da ingestão do arquivo. |

---

## Tabela: PUBLIC.NEIGHBOURHOODS (Regiões)
**Domínio:** Master Data Management (MDM)
**Origem:** PostgreSQL (Neon Serverless)
**Tipo de Carga:** Full Load (Replicação Total)

### Descrição do Negócio
Tabela de referência oficial (Lookup Table). Utilizada para garantir a integridade referencial dos nomes dos bairros e agrupar zonas geográficas.

Diferente dos dados de Reviews (que são logs de eventos), esta tabela muda muito pouco (Slowly Changing Dimension - Type 0 ou 1). Ela serve como "Fonte da Verdade" para os nomes dos locais.

### Estrutura de Colunas (Schema)

| Coluna | Classificação | Descrição Funcional |
| :--- | :--- | :--- |
| **neighbourhood** | `PK` (Natural) | Nome oficial do bairro. Deve corresponder exatamente ao campo `neighbourhood_cleansed` da tabela de Listings. |
| **neighbourhood_group** | `Agrupador` | (Se existir) Zona macro ou região administrativa do Rio de Janeiro a qual o bairro pertence. |