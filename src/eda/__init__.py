import os
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

PROCESSED_CSV = os.path.join(os.getcwd(), "data", "processed", "uber_dataset.csv")
EDA_OUTPUT_DIR = os.path.join(os.getcwd(), "data", "processed")

def run_eda():
    print("| Starting Exploratory Data Analysis...")
    
    if not os.path.exists(PROCESSED_CSV):
        print(f"| Processed data not found at {PROCESSED_CSV}. Run --process first.")
        return
        
    try:
        # Load dataset
        df = pd.read_csv(PROCESSED_CSV)
        print(f"| Loaded {len(df)} rows for analysis.")
        
        # Generate JSON summary
        summary = {
            "total_samples": len(df),
            "columns": list(df.columns),
            "ride_type_counts": df['ride_id'].value_counts().to_dict(),
            "average_price_per_ride_id": df.groupby('ride_id')['price'].mean().round(2).to_dict(),
            "average_wait_time_per_ride_id": df.groupby('ride_id')['wait_time_minutes'].mean().round(2).to_dict(),
            "price_stats": df['price'].describe().round(2).to_dict(),
            "routes_analyzed": df['route_name'].nunique()
        }
        
        json_path = os.path.join(EDA_OUTPUT_DIR, "eda_summary.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        print(f"    | EDA JSON summary saved to {json_path}")

        # Generate Plots
        sns.set_theme(style="whitegrid")
        
        # Plot 1: Price Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='price', hue='ride_id', kde=True, bins=30)
        plt.title("Distribuição de Preços por Categoria")
        plt.xlabel("Preço (R$)")
        plt.ylabel("Frequência")
        plt.savefig(os.path.join(EDA_OUTPUT_DIR, "eda_price_distribution.png"), bbox_inches='tight', dpi=150)
        plt.close()
        
        # Plot 2: Average Price by Hour
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='hour', y='price', hue='ride_id', marker='o', errorbar=None)
        plt.title("Média de Preços por Hora do Dia")
        plt.xlabel("Hora do Dia")
        plt.ylabel("Preço Médio (R$)")
        plt.xticks(range(0, 24))
        plt.savefig(os.path.join(EDA_OUTPUT_DIR, "eda_price_by_hour.png"), bbox_inches='tight', dpi=150)
        plt.close()
        
        # Plot 3: Wait Time Distribution (Boxplot)
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df, x='ride_id', y='wait_time_minutes', hue='ride_id', palette='Set2')
        plt.title("Tempo de Espera por Categoria")
        plt.xlabel("Categoria")
        plt.ylabel("Minutos de Espera")
        plt.savefig(os.path.join(EDA_OUTPUT_DIR, "eda_wait_time_boxplot.png"), bbox_inches='tight', dpi=150)
        plt.close()

        # Plot 4: Correlation Heatmap (numerical columns only)
        num_cols = ['price', 'wait_time_minutes', 'temperature_celsius', 'precipitation_mm', 'hour']
        plt.figure(figsize=(8, 6))
        sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title("Matriz de Correlação das Features")
        plt.savefig(os.path.join(EDA_OUTPUT_DIR, "eda_correlation_heatmap.png"), bbox_inches='tight', dpi=150)
        plt.close()

        print("    | EDA plots saved successfully as PNGs.")
        print("| EDA Phase Finished.")
        
    except Exception as e:
        print(f"| Error during EDA: {e}")