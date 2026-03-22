# src/database.py
import sqlite3
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSED, SEMAINE

# Connexion globale réutilisable
_conn = None

def creer_base(dfs):
    global _conn

    # Sur Streamlit Cloud, PROCESSED n'existe pas -> mémoire
    try:
        PROCESSED.mkdir(parents=True, exist_ok=True)
        db_path = str(PROCESSED / f"bi_{SEMAINE}.db")
    except Exception:
        db_path = ":memory:"

    _conn = sqlite3.connect(db_path, check_same_thread=False)

    tables = {
        "commandes_locales"   : dfs["locaux"],
        "commandes_etrangeres": dfs["etrangers"],
        "bc_clients"          : dfs["bc"],
        "ca_hebdo"            : dfs["ca"],
        "chantiers_en_cours"  : dfs["en_cours"],
        "chantiers_termines"  : dfs["termines"],
    }
    for nom, df in tables.items():
        df_sql = df.copy()
        for col in df_sql.columns:
            if pd.api.types.is_datetime64_any_dtype(df_sql[col]):
                df_sql[col] = df_sql[col].astype(str)
            elif df_sql[col].dtype == object:
                df_sql[col] = df_sql[col].apply(
                    lambda x: str(x) if pd.notna(x) and
                    not isinstance(x, (str, int, float)) else x
                )
        df_sql.to_sql(nom, _conn, index=False, if_exists="replace")

    print(f"Base SQLite : {len(tables)} tables chargées ({db_path})")

def sql(requete):
    return pd.read_sql_query(requete, _conn)

def ca_par_service():
    return sql("""
        SELECT Sce AS service,
               ROUND(SUM("Montant ht BC"), 0) AS ca_ht,
               COUNT(*) AS nb_factures
        FROM ca_hebdo
        GROUP BY Sce ORDER BY ca_ht DESC
    """)

def commandes_bloquees():
    return sql("""
        SELECT Fournisseur, "N° BC", Client,
               "Montant cde HT", Situation
        FROM commandes_locales
        WHERE LOWER(TRIM(Situation)) IN (
            'en attente de livraison','en traitement fseur',
            'sous douane','en cours')
        ORDER BY "Montant cde HT" DESC
    """)

def bc_factures_semaine():
    return sql("""
        SELECT bc.Clients, bc."Référence BC Clients",
               bc."Montant BC HT",
               ca."Réf facture clients",
               ca."Montant ht BC" AS montant_facture
        FROM bc_clients AS bc
        INNER JOIN ca_hebdo AS ca
            ON TRIM(bc."Référence BC Clients")
             = TRIM(ca."Référence BC Clients")
        ORDER BY montant_facture DESC
    """)