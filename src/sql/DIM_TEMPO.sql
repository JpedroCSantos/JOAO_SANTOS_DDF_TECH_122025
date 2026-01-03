CREATE OR REPLACE TABLE `ddf-olist-case-2025.airbnb_analytics.dim_tempo` AS
SELECT
  data AS DT_DATA,
  EXTRACT(YEAR FROM data) AS NR_ANO,
  EXTRACT(MONTH FROM data) AS NR_MES,
  FORMAT_DATE('%B', data) AS NM_MES, -- Nome do mês (ex: Janeiro)
  EXTRACT(DAY FROM data) AS NR_DIA,
  EXTRACT(DAYOFWEEK FROM data) AS NR_DIA_SEMANA, -- 1=Domingo, 7=Sábado
  FORMAT_DATE('%A', data) AS NM_DIA_SEMANA, -- Nome (ex: Monday)
  
  -- Flag de Final de Semana
  CASE 
    WHEN EXTRACT(DAYOFWEEK FROM data) IN (1, 7) THEN TRUE 
    ELSE FALSE 
  END AS FLG_FINAL_SEMANA,

  -- Flag de Feriado (Simplificado: Natal e Ano Novo)
  CASE
    WHEN EXTRACT(MONTH FROM data) = 12 AND EXTRACT(DAY FROM data) = 25 THEN TRUE
    WHEN EXTRACT(MONTH FROM data) = 1 AND EXTRACT(DAY FROM data) = 1 THEN TRUE
    ELSE FALSE
  END AS FLG_FERIADO

FROM 
  UNNEST(GENERATE_DATE_ARRAY('2010-01-01', '2030-12-31')) AS data;