import os
import pandas as pd
from utils import read_row_datetime, calcul_nom_colonne


def load_datafficheur_file(fichier: str, verbose: bool = False):
    """
    Charge un fichier CSV, effectue des transformations sur les donnees et retourne le DataFrame resultant.

    Args:
        fichier (str): Chemin vers le fichier e charger.
        verbose (bool): Si vrai, affiche des messages supplementaires lors du traitement.

    Returns:
        pandas.DataFrame: Le DataFrame contenant les donnees chargees et transformees.

    Raises:
        FileNotFoundError: Si le fichier specifie n'existe pas.
        pd.errors.ParserError: Si le fichier ne peut pas etre correctement lu comme un CSV.
    """
    if verbose:
        print(f"Traitement du fichier {fichier}")

    try:
        datas_fichier = pd.read_csv(fichier, header=None)
    except FileNotFoundError:
        print(f"Le fichier {fichier} n'a pas ete trouve.")
        raise
    except pd.errors.ParserError:
        print(f"Erreur lors de l'analyse du fichier {fichier}.")
        raise

    datas_fichier.set_index([0, 1, 2], inplace=True)
    datas_fichier.columns = pd.MultiIndex.from_tuples(
        map(calcul_nom_colonne, range(len(datas_fichier.columns)))
    )
    datas_fichier = datas_fichier.stack(level=0)
    datas_fichier.index = [read_row_datetime(row) for row in datas_fichier.index]

    return datas_fichier


def add_notes(df, dir, note, verbose=False):
    """
    Ajoute des notes e un DataFrame sur un intervalle de temps specifique.

    Args:
        df (pandas.DataFrame): Le DataFrame auquel ajouter les notes.
        dir (str): Le repertoire oe se trouve le fichier contenant les notes.
        note (str): Le nom du fichier contenant les notes.
        verbose (bool, optional): Si vrai, affiche des messages supplementaires pendant le processus. Par defaut : False.

    Returns:
        pandas.DataFrame: Le DataFrame avec les notes ajoutees.

    Raises:
        ValueError: Si df n'est pas un DataFrame pandas, ou si le fichier des notes ne contient pas les colonnes 'start', 'end' et 'action'.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df doit etre un DataFrame pandas.")

    if verbose:
        print(f"Chargement des notes {note}")
    notecols = ["start", "end", "action"]
    note_metadata = pd.read_csv(os.path.join(dir, note), header=None, names=notecols)
    if not {"start", "end", "action"}.issubset(note_metadata.columns):
        raise ValueError(
            "Le fichier des notes doit contenir les colonnes 'start', 'end' et 'action'."
        )

    if verbose:
        print(note_metadata)

    for index, row in note_metadata.iterrows():
        if verbose:
            print(
                f"Ajout de l'action sur l'interval {row['start']}-{row['end']}: {row['action']}"
            )
        df.loc[row["start"] : row["end"], "action"] = row["action"]

    return df


def prepare_data(data):
    """
    Prepare les donnees pour une analyse ulterieure en regroupant et en sommant les colonnes.

    Args:
        data (pandas.DataFrame): Le DataFrame e preparer.

    Returns:
        pandas.DataFrame: Le DataFrame prepare.

    Raises:
        ValueError: Si data n'est pas un DataFrame pandas.
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit etre un DataFrame pandas.")

    df = {}
    for col in data.columns:
        df[col] = pd.DataFrame(data={"Efforts": data[col]}, index=data.index)
        df[col].index.name = "date"
    df = pd.concat(df, axis=1)
    df_total = df.groupby(axis=1, level=1).sum()
    for col in df_total.columns:
        df[("Total", col)] = df_total[col]

    return df
