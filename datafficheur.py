import argparse
import os
import pathlib
import pytz
import re
from glob import glob
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Constante
DEFAULT_TIMEZONE = "Europe/Paris"

# traitement des arguments
parser = argparse.ArgumentParser(
    prog="Datafficheur",
    description="Lecture des donnees du capteur Datafficheur. http://hippotese.free.fr/blog/index.php/?q=datafficheur",
)
requiredNamed = parser.add_argument_group("required arguments")
requiredNamed.add_argument(
    "-d",
    "--dir",
    help="Chemin vers le dossier contenant les donnees Datafficheur.",
    required=True,
    type=pathlib.Path,
)
parser.add_argument(
    "-n",
    "--note",
    help=f"Fichier indiquant les temps de debut et fin et le type d'outil. Par defaut: note.csv",
    default="note.csv",
)
parser.add_argument(
    "-v", "--verbose", help="Affiche des messages sur la progression.", default=True
)
parser.add_argument(
    "-o",
    "--output",
    help=f"Nom du fichier cree. Par defaut: output.csv",
    default="output.csv",
)
parser.add_argument(
    "-p",
    "--plot",
    help=f"Creation d'un graphique.",
    action=argparse.BooleanOptionalAction,
    default=True,
)
parser.add_argument(
    "-op",
    "--outputplot",
    help=f"Sauvegarde du graphique (eg. format PDF, PNG, SVG). Par defaut: None",
    default=None,
)
parser.add_argument(
    "-z",
    "--timezone",
    help=f"Fuseau horaire. Par defaut: {DEFAULT_TIMEZONE}",
)

args = parser.parse_args()

# definition de la timezone
tz = DEFAULT_TIMEZONE
try:
    tz = pytz.timezone(args.timezone)
except pytz.exceptions.UnknownTimeZoneError:
    if args.verbose:
        print(f"TimeZone inconnu. utilisation de {DEFAULT_TIMEZONE}")
    tz = DEFAULT_TIMEZONE

output = args.output
note = args.note
dir = args.dir
hasNote = os.path.exists(os.path.join(dir, note))
plot = args.plot
outputplot = args.outputplot
verbose = args.verbose


def find_files(directory):
    """
    Cherche et retourne une liste des fichiers dans le dossier specifie
    dont le nom correspond e une expression reguliere.

    L'expression reguliere utilisee est r'[0-9]{8}.txt$',
    ce qui signifie que la fonction cherche des fichiers
    qui ont un nom de 8 chiffres (de 0 e 9), suivi par l'extension '.txt'.

    Args:
        directory (str): Le chemin du dossier dans lequel chercher les fichiers.

    Returns:
        list: Une liste contenant les noms de tous les fichiers correspondant e l'expression reguliere
        dans le dossier specifie. Si aucun fichier ne correspond, la fonction retourne une liste vide.
    """
    pattern = re.compile(r"[0-9]{8}.txt$", re.IGNORECASE)
    return [
        os.path.join(directory, f) for f in os.listdir(directory) if pattern.match(f)
    ]


def read_row_datetime(row):
    """
    Reconstitue le datetime d'une ligne du fichier brut avec la date
    (colonne 1), l'heure (colonne 2) et la deciseconde (colonne 3)
    """
    return datetime.strptime(
        row[1] + " " + row[2] + "." + str(row[3]), "%d/%m/%Y %H:%M:%S.%f"
    )


def calcul_nom_colonne(x, frequence_acquisition=10):
    """
    Calcule la fraction de seconde et le numero du capteur en fonction
    de l'index de l'echantillon et de la frequence d'acquisition.

    Args:
        x (int): Index de l'echantillon.
        frequence_acquisition (int): Nombre d'echantillons par seconde. Doit etre positif. Par defaut : 10.

    Returns:
        tuple: Un tuple (fraction_seconde, numero_capteur).

    Raises:
        ValueError: Si x ou frequence_acquisition est negatif, ou si frequence_acquisition est zero.
    """
    if x < 0 or frequence_acquisition <= 0:
        raise ValueError(
            "x et frequence_acquisition doivent etre positifs. frequence_acquisition doit etre different de zero."
        )

    fraction_seconde = x % frequence_acquisition
    numero_capteur = x // frequence_acquisition + 1
    return (fraction_seconde, numero_capteur)


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


def moving_average(x, w):
    """
    Calcule la moyenne mobile d'une liste de nombres.

    Args:
        x (list of number): La liste de nombres sur laquelle calculer la moyenne mobile.
        w (int): La taille de la fenetre de la moyenne mobile.

    Returns:
        numpy.array: Un array numpy contenant les valeurs de la moyenne mobile.

    Raises:
        ValueError: Si w est zero ou negatif, ou si x est une liste vide.
    """
    if not x:
        raise ValueError("x ne peut pas etre une liste vide.")
    if w <= 0:
        raise ValueError("w doit etre un entier positif.")
    if w > len(x):
        raise ValueError("w ne peut pas etre plus grand que la longueur de x.")

    return np.convolve(x, np.ones(w), mode="same") / w


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


def create_plot(df, timezone, outputplot=None, verbose=False):
    """
    Cree un graphique e partir des donnees fournies et l'enregistre dans un fichier si specifie.

    Args:
        df (pandas.DataFrame): Le DataFrame e representer graphiquement.
        timezone (str): Le fuseau horaire e utiliser pour le graphique.
        outputplot (str, optional): Le nom du fichier oe sauvegarder le graphique. Si None, le graphique est affiche. Par defaut : None.
        verbose (bool, optional): Si vrai, affiche des messages supplementaires pendant la creation du graphique. Par defaut : False.

    Returns:
        None

    Raises:
        ValueError: Si df n'est pas un DataFrame pandas ou si outputplot n'est pas une chaene de caracteres.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df doit etre un DataFrame pandas.")
    if outputplot is not None and not isinstance(outputplot, str):
        raise ValueError("outputplot doit etre une chaene de caracteres.")

    plt.figure(figsize=(19.20, 10.80), dpi=200)

    plt.gca().xaxis_date(timezone)
    plt.plot(df, label=df.columns, alpha=0.5)

    max_y = df.max().max()  # Obtient la valeur maximale dans le DataFrame
    plt.yticks(np.arange(0, max_y, 25))  # Definit les ticks de l'axe des y tous les 25
    plt.grid(
        axis="y", linestyle="dotted"
    )  # Dessine une grille horizontale en pointilles

    plt.legend()
    plt.title("DATAFFICHEUR - Effort en fonction du temps")
    plt.xlabel("Temps")
    plt.ylabel("kgf (kilogramme force - equivalant daN)")
    if outputplot:
        if verbose:
            print(f"Export du graphique dans {outputplot}.")
        plt.savefig(outputplot)
        plt.close()  # Ferme la figure pour liberer de la memoire
    else:
        plt.show()


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


def main(dir, hasNote, note, plot, verbose, outputplot, tz, output):
    """
    Fonction principale qui execute la chaene de traitement de donnees.

    Args:
        dir (str): Le repertoire contenant les fichiers de donnees.
        hasNote (bool): Indique s'il faut ajouter des notes aux donnees.
        note (str): Le nom du fichier contenant les notes.
        plot (bool): Indique si un graphique doit etre cree.
        verbose (bool): Si vrai, affiche des messages supplementaires pendant le processus.
        outputplot (str): Le chemin du fichier de sortie pour le graphique.
        tz (str): Le fuseau horaire e utiliser pour l'affichage des dates.
        output (str): Le nom du fichier de sortie.
    """

    try:
        # liste les fichiers sources
        fichiers = find_files(dir)
        if len(fichiers) == 0:
            print(f"Aucun fichier de donnees dans {dir}")
            exit()

        # aggregation des datas
        datas_par_fichier = [load_datafficheur_file(fichier) for fichier in fichiers]
        concatenated_datas = pd.concat(datas_par_fichier)
        # On trie et suppression des doublons
        sorted_datas = concatenated_datas.sort_index()
        datas = sorted_datas[~sorted_datas.index.duplicated("first")]

        df = prepare_data(datas)

        # ajout des notes au dataframe si existe
        if hasNote:
            df = add_notes(df, dir, note, verbose)

        # creation des fichier
        if plot:
            if verbose:
                print("Creation du graphique.")
            create_plot(
                df, tz, os.path.join(dir, outputplot) if outputplot else None, verbose
            )

        df.columns = [" ".join(str(level) for level in col) for col in df.columns]
        df.index = pd.MultiIndex.from_arrays(
            [df.index.date, [t.strftime("%H:%M:%S.%f")[:10] for t in df.index.time]],
            names=["date", "heure"],
        )

        if verbose:
            print(f"Ecriture du fichier de sortie {output}")
        df.to_csv(os.path.join(dir, output))

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


if __name__ == "__main__":
    main(dir, hasNote, note, plot, verbose, outputplot, tz, output)
