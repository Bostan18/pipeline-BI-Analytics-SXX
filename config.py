from pathlib import Path

# --- Paramètre à cahnger chaque semaine ---
SEMAINE = "s12"  # Seule ligne à modifier chaque semane

# --- Chemins (ne pas modifier) ---

RACINE        = Path(r"C:\Projects\bi-analytics")
RAW           = RACINE / "data" / "raw"
PROCESSED     = RACINE / "data" / "processed"
OUTPUT        = RACINE / "output"

# Construction des chemains
CMD = RAW / f"suivi_commandes_{SEMAINE}.xlsx"
CHT = RAW / f"suivi_chantiersCT_{SEMAINE}.xlsx"

# --- Noms de feuilles ---
FEUILLES_CMD = {
    "locaux"    : "Fsrs locaux",
    "etrangers" : "Fsrs Etrangers",
    "bc"        : "BC Clients",
    "ca"        : "CA Hebdo",
}
FEUILLES_CHT = {
    "en_cours"  : "Projet en cours 00-99%",
    "termines"  : "Projet 100% Implémenté",
    "t1"        : "T1",
}

# --- Colonne commentaires (change av ec la semaine) ---
COL_NOTES = f"Notes / Commentaires de {SEMAINE.upper()}"