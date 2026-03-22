import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import SEMAINE
from src.extract import lire_feuille, nettoyer, FEUILLES_CMD, FEUILLES_CHT
from src.transform import calculer_kpis
from src.database import creer_base, ca_par_service, commandes_bloquees

st.set_page_config(
    page_title="BI Dashboard — Rapport Hebdomadaire",
    page_icon="📊",
    layout="wide"
)

# --- Sidebar : upload des fichiers ---
st.sidebar.title("Fichiers de la semaine")
st.sidebar.caption("Déposez les deux fichiers Excel reçus par mail.")

f_cmd = st.sidebar.file_uploader(
    "Fichier ADV (suivi_commandes_sXX.xlsx)",
    type=["xlsx"],
    key="cmd"
)
f_cht = st.sidebar.file_uploader(
    "Fichier Service Client (suivi_chantiersCT_sXX.xlsx)",
    type=["xlsx"],
    key="cht"
)

# Détecter la semaine depuis le nom du fichier
semaine = SEMAINE.upper()
if f_cmd is not None:
    nom = f_cmd.name.lower()
    for part in nom.replace(".", "_").split("_"):
        if part.startswith("s") and part[1:].isdigit():
            semaine = part.upper()
            break

# --- Attendre les deux fichiers ---
if f_cmd is None or f_cht is None:
    st.title("📊 BI Analytics — Rapport Hebdomadaire")
    st.info(
        "Déposez les deux fichiers Excel dans la barre latérale gauche "
        "pour générer le rapport."
    )
    st.stop()

# --- Chargement des données ---
@st.cache_data
def charger_depuis_upload(cmd_bytes, cht_bytes, semaine):
    cmd_buf = io.BytesIO(cmd_bytes)
    cht_buf = io.BytesIO(cht_bytes)

    def lire(buf, feuille, header=5):
        buf.seek(0)
        return nettoyer(lire_feuille(buf, feuille, header))

    dfs = {
        "locaux"   : lire(cmd_buf, FEUILLES_CMD["locaux"]),
        "etrangers": lire(cmd_buf, FEUILLES_CMD["etrangers"]),
        "bc"       : lire(cmd_buf, FEUILLES_CMD["bc"]),
        "ca"       : lire(cmd_buf, FEUILLES_CMD["ca"]),
        "en_cours" : lire(cht_buf, FEUILLES_CHT["en_cours"]),
        "termines" : lire(cht_buf, FEUILLES_CHT["termines"]),
        "t1"       : pd.read_excel(cht_buf, sheet_name="T1",
                                   engine="calamine"),
    }
    kpis = calculer_kpis(dfs, semaine=semaine)
    creer_base(dfs)
    return dfs, kpis

dfs, kpis = charger_depuis_upload(
    f_cmd.getvalue(), f_cht.getvalue(), semaine
)

# DEBUG — à supprimer après
st.write("Semaine détectée :", semaine)
st.write("Colonnes termines :", dfs["termines"].columns.tolist())

col_n = f"Notes / Commentaires de {semaine}"

# --- En-tête ---
st.title(f"📊 Rapport hebdomadaire — Semaine {semaine}")
st.caption("Généré automatiquement depuis les fichiers ADV et Service Client")

# --- KPIs ---
st.subheader("Indicateurs clés")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("CA HT",  f"{kpis['ca_ht']/1e6:.1f}M")
c2.metric("CA TTC", f"{kpis['ca_ttc']/1e6:.1f}M")
c3.metric("Commandes bloquées",
          kpis['nb_loc_bloque'] + kpis['nb_etr_bloque'],
          f"{kpis['nb_loc_bloque']} loc. + {kpis['nb_etr_bloque']} etr.",
          delta_color="inverse")
c4.metric("Chantiers en retard", kpis['nb_retard'],
          delta_color="inverse")
c5.metric("Fact. partielles", kpis['nb_partiel'],
          delta_color="inverse")

st.divider()

# --- Graphiques ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("CA HT par service")
    ca = (dfs["ca"].groupby("Sce")["Montant ht BC"]
          .sum().dropna().sort_values(ascending=True))
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.barh(ca.index, ca.values,
                   color=["#378ADD", "#1D9E75", "#EF9F27"])
    for bar, val in zip(bars, ca.values):
        ax.text(val + 300_000, bar.get_y() + bar.get_height() / 2,
                f"{val/1e6:.1f}M", va="center", fontsize=9)
    ax.set_xlabel("FCFA")
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("Chantiers les moins avancés")
    col_av, col_cli = "% d'exécution", "Client"
    df_ch = dfs["en_cours"][[col_cli, col_av]].copy()
    df_ch[col_av] = pd.to_numeric(df_ch[col_av], errors="coerce")
    df_ch = df_ch.dropna(subset=[col_av])
    if df_ch[col_av].max() <= 1.0:
        df_ch[col_av] = df_ch[col_av] * 100
    df_ch = df_ch[(df_ch[col_av] > 0) & (df_ch[col_av] < 100)]
    df_ch = df_ch.sort_values(col_av).head(10)
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    couleurs = ["#E24B4A" if v < 50 else "#EF9F27" for v in df_ch[col_av]]
    ax2.barh(df_ch[col_cli], df_ch[col_av], color=couleurs)
    ax2.axvline(x=50, color="gray", linestyle="--", linewidth=0.8)
    ax2.set_xlim(0, 110)
    ax2.set_xlabel("% d'avancement")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

st.divider()

# --- Tableaux ---
st.subheader("CA par service (SQL)")
st.dataframe(ca_par_service(), use_container_width=True)

st.subheader("Commandes bloquées")
st.dataframe(commandes_bloquees(), use_container_width=True)

st.subheader("Chantiers en cours")
st.dataframe(
    dfs["en_cours"][["Client", "Intitulé du projet",
                     "% d'exécution", "Domaine d'activité", col_n]]
    .sort_values("% d'exécution"),
    use_container_width=True
)

st.subheader("Projets terminés — facturation partielle")
st.dataframe(
    dfs["termines"][
        dfs["termines"][col_n].str.contains(
            "partielle", case=False, na=False)
    ][["Client", "Intitulé du projet", col_n]],
    use_container_width=True,
    hide_index=True
)