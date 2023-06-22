import argparse
import os
import pytz
import pathlib
import pandas as pd
from constants import DEFAULT_TIMEZONE
from data_processing import load_datafficheur_file, add_notes, prepare_data
from plotting import create_plot
from utils import find_files, moving_average

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
    "-pht",
    "--plothticks",
    type=int,
    help=f"Segmentation de l'axe Y",
    default=10,
)
parser.add_argument(
    "-z",
    "--timezone",
    help=f"Fuseau horaire. Par defaut: {DEFAULT_TIMEZONE}",
)

args = parser.parse_args()

# definition de la timezone
tz = args.timezone
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

        # collecte de la date de mesure pour intégration (titre graph + filename)
        unique_dates = pd.Series(df.index.date).unique()
        # Obtenir les dates minimale et maximale
        min_date = unique_dates.min()
        max_date = unique_dates.max()
        date_str = ""
        # si les mesures sont sur plus d'un jour ...
        if len(unique_dates) > 1:
            # ... on prend min et max
            date_str = f"{min_date} - {max_date}"
        else:
            # ... sinon just min
            date_str = f"{min_date}"

        # ajout des notes au dataframe si existe
        if hasNote:
            df = add_notes(df, dir, note, verbose)

        # creation des fichier
        if plot:
            if verbose:
                print("Creation du graphique.")
            create_plot(
                df,
                tz,
                os.path.join(dir, date_str + "_" + outputplot) if outputplot else None,
                verbose,
                args.plothticks,
                date_str,
            )

        df.columns = [" ".join(str(level) for level in col) for col in df.columns]
        df.index = pd.MultiIndex.from_arrays(
            [df.index.date, [t.strftime("%H:%M:%S.%f")[:10] for t in df.index.time]],
            names=["date", "heure"],
        )

        if verbose:
            print(f"Ecriture du fichier de sortie {date_str}_{output}")
        df.to_csv(os.path.join(dir, date_str + "_" + output))

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


if __name__ == "__main__":
    main(dir, hasNote, note, plot, verbose, outputplot, tz, output)
