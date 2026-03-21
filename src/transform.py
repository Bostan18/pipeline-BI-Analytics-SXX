import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COL_NOTES

def calculer_kpis(dfs):

    # --- Récupération depuis le dictionnaire ---
    df_ca  = dfs["ca"].copy()
    df_loc = dfs["locaux"].copy()
    df_etr = dfs["etrangers"].copy()
    df_enc = dfs["en_cours"].copy()
    df_100 = dfs["termines"].copy()

    # --- Nettoyage noms de colonnes ---
    df_loc["Situation"] = df_loc["Situation"].str.strip().str.lower()
    df_etr["Situation"] = df_etr["Situation"].str.strip().str.lower()
    df_enc = df_enc.rename(columns={
        "Estimé\nDébut" : "debut_estime",
        "Estimé \nFin"  : "fin_estimee",
        "Réel \nDébut"  : "debut_reel",
        "% d'exécution" : "avancement",
    })

    # --- KPI 1 : CA semaine ---
    ca_ht  = df_ca["Montant ht BC"].sum()
    ca_ttc = df_ca["Montant TTC"].sum()

    # --- KPI 2 : Commandes bloquées ---
    en_attente = ["en attente de livraison", "en traitement fseur",
                  "sous douane", "en cours"]
    nb_loc_bloque = df_loc[df_loc["Situation"].isin(en_attente)].shape[0]
    nb_etr_bloque = df_etr[df_etr["Situation"].isin(en_attente)].shape[0]

    # --- KPI 3 : Chantiers en retard ---
    now = pd.Timestamp("today")
    nb_retard = df_enc[
        (df_enc["fin_estimee"] < now) & (df_enc["avancement"] < 1.0)
    ].shape[0]

    # --- KPI 4 : Projets 100% à facturation partielle ---
    nb_partiel = df_100[
        df_100[COL_NOTES].str.contains("partielle", case=False, na=False)
    ].shape[0]

    # --- KPI 5 : CA par service ---
    ca_par_service = (
        df_ca.groupby("Sce")["Montant ht BC"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    ca_par_service.columns = ["Service", "CA HT"]
    ca_par_service["Part %"] = (
        ca_par_service["CA HT"] / ca_ht * 100
    ).round(1)

    return {
        "ca_ht"        : ca_ht,
        "ca_ttc"       : ca_ttc,
        "nb_loc_bloque": nb_loc_bloque,
        "nb_etr_bloque": nb_etr_bloque,
        "nb_retard"    : nb_retard,
        "nb_partiel"   : nb_partiel,
    }



