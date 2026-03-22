from pathlib import Path

SEMAINE = "s11"

# Chemin relatif au fichier config.py lui-même — fonctionne partout
RACINE    = Path(__file__).parent
RAW       = RACINE / "data" / "raw"
PROCESSED = RACINE / "data" / "processed"
OUTPUT    = RACINE / "output"

CMD = RAW / f"suivi_commandes_{SEMAINE}.xlsx"
CHT = RAW / f"suivi_chantiersCT_{SEMAINE}.xlsx"

FEUILLES_CMD = {
    "locaux"   : "Fsrs locaux",
    "etrangers": "Fsrs Etrangers",
    "bc"       : "BC Clients",
    "ca"       : "CA Hebdo",
}
FEUILLES_CHT = {
    "en_cours" : "Projet en cours 00-99%",
    "termines" : "Projet 100% Implémenté",
    "t1"       : "T1",
}

COL_NOTES = f"Notes / Commentaires de {SEMAINE.upper()}"