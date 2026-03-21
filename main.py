import time
from src.extract   import charger_donnees
from src.transform import calculer_kpis
from src.database  import creer_base, ca_par_service, commandes_bloquees
from src.report    import generer
from config        import SEMAINE, OUTPUT

def main():
    debut = time.time()
    semaine = SEMAINE

    print(f"{'='*44}")
    print(f"  PIPELINE BI - SEMAINE {semaine}")
    print(f"{'='*44}")

    print("\n[1/4] Chargement des données...")
    dfs = charger_donnees()

    print("\n[2/4] Calcul des KPIs...")
    kpis = calculer_kpis(dfs)

    print("[3/4] Requêtes SQL...")
    creer_base(dfs)
    print("\n--- CA par service ---")
    print(ca_par_service().to_string(index=False))
    print("\n--- Top commandes bloquées ---")
    print(commandes_bloquees().head(5).to_string(index=False))

    print("\n[4/4] Génération du rapport...")
    generer(dfs, kpis)

    duree = time.time() - debut

    print(f"\n{'='*44}")
    print(f"  RÉSUMÉ {semaine}")
    print(f"{'='*44}")
    print(f"  CA HT réalisé       : {kpis['ca_ht']:>12,.0f} FCFA")
    print(f"  CA TTC réalisé      : {kpis['ca_ttc']:>12,.0f} FCFA")
    print(f"  Commandes bloquées  : {kpis['nb_loc_bloque'] + kpis['nb_etr_bloque']:>12} ({kpis['nb_loc_bloque']} loc. + {kpis['nb_etr_bloque']} etr.)")
    print(f"  Chantiers en retard : {kpis['nb_retard']:>12} projets")
    print(f"  Fact. partielles    : {kpis['nb_partiel']:>12} projets terminés")
    print(f"\n  Fichiers générés    : {OUTPUT}")
    print(f"  Durée totale        : {duree:.1f}s")
    print(f"{'='*44}\n")

if __name__ == "__main__":
    main()