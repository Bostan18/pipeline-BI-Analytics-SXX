# Chargement des données
import pandas as pd
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CMD, CHT, FEUILLES_CMD, FEUILLES_CHT

# Fonction réutilisable pour toutes les feuilles avec header décalé
def lire_feuille(fichier, feuille, header=5):
    xl = pd.ExcelFile(fichier, engine="calamine")
    noms = xl.sheet_names
    correspondance = next((n for n in noms
                            if n.strip() == feuille.strip()), None)
    if correspondance is None:
        raise ValueError(f"Feuille '{feuille}' introuvable. Disponibles : {noms}")
    return pd.read_excel(fichier, sheet_name=correspondance,
                         header=header, engine="calamine")


def nettoyer(df):
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df = df[[c for c in df.columns if not str(c).startswith("Unnamed")]]
    df.columns = df.columns.str.strip()
    return df.reset_index(drop=True)

def charger_donnees():
    # Vérification avant lncement
    assert CMD.exists(), f"Fichier introuvable : {CMD}"
    assert CHT.exists(), f"Fichier introuvable : {CHT}"

    return {
        "locaux"    : nettoyer(lire_feuille(CMD, FEUILLES_CMD["locaux"])),
        "etrangers" : nettoyer(lire_feuille(CMD, FEUILLES_CMD["etrangers"])),
        "bc"        : nettoyer(lire_feuille(CMD, FEUILLES_CMD["bc"])),
        "ca"        : nettoyer(lire_feuille(CMD, FEUILLES_CMD["ca"])),
        "en_cours"  : nettoyer(lire_feuille(CHT, FEUILLES_CHT["en_cours"])),
        "termines"  : nettoyer(lire_feuille(CHT, FEUILLES_CHT["termines"])),
        "t1"        : pd.read_excel(CHT, sheet_name="T1", engine="calamine"),
    }


if __name__ == "__main__":
    dfs = charger_donnees()
    for nom, df in dfs.items():
        print(f"{nom:<12} : {df.shape[0]:>} lignes | {df.shape[1]} colonnes")