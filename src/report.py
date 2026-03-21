import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT, SEMAINE

def generer(dfs, kpis):
    OUTPUT.mkdir(exist_ok=True)
    graphique_ca_service(dfs["ca"], SEMAINE, OUTPUT)
    graphique_chantiers(dfs["en_cours"], SEMAINE, OUTPUT)
    exporter_excel(dfs, kpis , SEMAINE, OUTPUT)
    print(f"\nRapport S11 généré dans : {OUTPUT}")

def graphique_ca_service(df_ca, semaine, OUTPUT):
    ca = (df_ca.groupby("Sce")["Montant ht BC"]
                .sum().dropna().sort_values(ascending=True))
    fig, ax = plt.subplots(figsize=(8, 4))          # bug 1 : subplots
    bars = ax.barh(ca.index, ca.values,             # bug 2 : values
                   color=["#378ADD", "#1D9E75", "#EF9F27"])
    for bar, val in zip(bars, ca.values):
        ax.text(val + 500_000, bar.get_y() + bar.get_height() / 2,
                f"{val/1_000_000:.1f}M", va="center", fontsize=10)
    ax.set_title(f"CA HT par service - {semaine.upper()}",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("FCFA")
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
    plt.tight_layout()
    p = OUTPUT / f"ca_service_{semaine}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG : {p.name}")

def graphique_chantiers(df_enc, semaine, output):
    col_av  = "% d'exécution"
    col_cli = "Client"

    df = df_enc[[col_cli, col_av]].copy()
    df[col_av] = pd.to_numeric(df[col_av], errors="coerce")
    df = df.dropna(subset=[col_av])

    # Multiplier par 100 si valeurs entre 0 et 1
    if df[col_av].max() <= 1.0:
        df[col_av] = df[col_av] * 100

    # Garder uniquement les chantiers en cours (entre 1% et 99%)
    df = df[(df[col_av] > 0) & (df[col_av] < 100)]
    df = df.sort_values(col_av).head(10)

    fig, ax = plt.subplots(figsize=(8, 5))
    couleurs = ["#E24B4A" if v < 50 else "#EF9F27" for v in df[col_av]]
    bars = ax.barh(df[col_cli], df[col_av], color=couleurs)

    for bar, val in zip(bars, df[col_av]):
        ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}%", va="center", fontsize=9)

    ax.axvline(x=50, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlim(0, 110)
    ax.set_xlabel("% d'avancement")
    ax.set_title(f"Chantiers les moins avancés - {semaine.upper()}",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    p = output / f"chantiers_{semaine}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG : {p.name}")


def exporter_excel(dfs, kpis, semaine, output):
    chemin = output / f"rapport_{semaine}.xlsx"
    with pd.ExcelWriter(chemin, engine="openpyxl") as writer:
        pd.DataFrame([
            {"Indicateur": "CA HT",          "Valeur": f"{kpis['ca_ht']:,.0f}"},
            {"Indicateur": "CA TTC",         "Valeur": f"{kpis['ca_ttc']:,.0f}"},
            {"Indicateur": "Cdes bloquées",  "Valeur": kpis["nb_loc_bloque"]},
            {"Indicateur": "En retard",      "Valeur": kpis["nb_retard"]},
            {"Indicateur": "Fact. partielle","Valeur": kpis["nb_partiel"]},
        ]).to_excel(writer, sheet_name="KPIs", index=False)
        dfs["ca"].to_excel(writer, sheet_name="CA Hebdo", index=False)
        dfs["locaux"][
            dfs["locaux"]["Situation"].str.lower()
               .isin(["en attente de livraison", "en traitement fseur",
                      "sous douane", "en cours"])
        ].to_excel(writer, sheet_name="Cdes bloquées", index=False)
    print(f" Excel : {chemin.name}")