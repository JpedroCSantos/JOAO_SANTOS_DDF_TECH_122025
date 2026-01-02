import pandas as pd
import os

PROJECT_ID = "ddf-olist-case-2025"
DATASET_ID = "airbnb_analytics"

# Caminhos locais dos seus arquivos gerados (Gold/Silver)
PATH_LISTINGS = "data/silver/dim_listings.csv" 
PATH_REVIEWS = "data/silver/fact_reviews.csv"
# Se tiver o enriquecido da IA, adicione aqui também
PATH_LISTINGS_ENRICHED = "data/gold/fact_listings_enriched.csv"
PATH_REVIEWS_ENRICHED = "data/gold/fact_reviews_enriched.csv"

def upload_local_to_bq(file_path, table_name):
    print(f"🚀 Iniciando upload de {file_path} para {table_name}...")
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return

    df = pd.read_csv(file_path)
    df.to_gbq(
        destination_table=f"{DATASET_ID}.{table_name}",
        project_id=PROJECT_ID,
        if_exists='replace', # 'replace' recria a tabela. Use 'append' para adicionar.
        progress_bar=True
    )
    print(f"✅ Sucesso! Tabela {DATASET_ID}.{table_name} criada.")

if __name__ == "__main__":
    upload_local_to_bq(PATH_LISTINGS, "dim_listings")
    upload_local_to_bq(PATH_REVIEWS, "fact_reviews")


    upload_local_to_bq(PATH_LISTINGS_ENRICHED, "fact_listings_enriched")
    upload_local_to_bq(PATH_REVIEWS_ENRICHED, "fact_reviews_enriched")
    print("\n🏁 Carga completa! Verifique no BigQuery Console.")