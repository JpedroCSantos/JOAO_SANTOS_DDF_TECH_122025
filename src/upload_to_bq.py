import pandas as pd
import os

PROJECT_ID = "ddf-olist-case-2025"
DATASET_ID = "airbnb_analytics"

# Caminhos locais dos seus arquivos gerados (Gold/Silver)
PATH_LISTINGS = "data/silver/silver_dim_listings.csv" 
PATH_REVIEWS = "data/silver/silver_fact_reviews.csv"
PATH_LISTINGS_ENRICHED = "data/gold/DIM_LISTINGS.csv"
PATH_REVIEWS_ENRICHED = "data/gold/FACT_REVIEWS.csv"

def upload_local_to_bq(file_path, table_name):
    print(f"Iniciando upload de {file_path} para {table_name}...")
    
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return

    df = pd.read_csv(file_path)
    df.to_gbq(
        destination_table=f"{DATASET_ID}.{table_name}",
        project_id=PROJECT_ID,
        if_exists='replace',
        progress_bar=True
    )
    print(f"✅ Sucesso! Tabela {DATASET_ID}.{table_name} criada.")

if __name__ == "__main__":
    upload_local_to_bq(PATH_LISTINGS, "silver_dim_listings")
    upload_local_to_bq(PATH_REVIEWS, "silver_fact_reviews")


    upload_local_to_bq(PATH_LISTINGS_ENRICHED, "DIM_LISTINGS")
    upload_local_to_bq(PATH_REVIEWS_ENRICHED, "FACT_REVIEWS")
    print("\n🏁 Carga completa! Verifique no BigQuery Console.")