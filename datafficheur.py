import argparse
import numpy as np
import os.path
import pandas as pd
import pathlib
import pytz
from datetime import datetime
from glob import glob
from matplotlib import pyplot as plt


class Datafficheur:
    DEFAULT_TIMEZONE = "Europe/Paris"
    timezone = None
    output = "output.csv"
    dir = None
    plot = True
    outputplot = None
    # outputplot = "output.pdf"
    verbose = True

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="Datafficheur",
            description="Lecture des données du capteur Datafficheur. http://hippotese.free.fr/blog/index.php/?q=datafficheur"
        )
        parser.add_argument("-d", "--dir",
                            help="Chemin vers le dossier contenant les données Datafficheur.",
                            type=pathlib.Path)
        parser.add_argument("-v", "--verbose",
                            help="Affiche des messages sur la progression.",
                            default=self.verbose)
        parser.add_argument("-o", "--output",
                            help=f"Nom du fichier créé. Par défaut: {self.output}",
                            default=self.output)
        parser.add_argument("-p", "--plot",
                            help=f"Création d'un graphique. Par défaut: {self.plot}",
                            default=self.plot)
        parser.add_argument("-op", "--outputplot",
                            help=f"Sauvegarde du graphique (eg. format PDF, PNG, SVG). Par défaut: {self.outputplot}",
                            default=self.outputplot)
        parser.add_argument("-z", "--timezone",
                            help=f"Fuseau horaire. Par défaut: {self.DEFAULT_TIMEZONE}",
                            default=self.DEFAULT_TIMEZONE)

        args = parser.parse_args()
        self.dir = args.dir
        self.output = args.output
        self.plot = args.plot
        self.outputplot = args.outputplot
        self.verbose = args.verbose
        self.timezone = pytz.timezone(args.timezone)

        # Pattern pour retrouver les fichiers datafficheur dans le dossier de travail
        # os.path.join permet de reconstituer le chemin d'accès sans se soucier du séparateur "/" ou "\" qui peut différer entre unix et windows
        pattern = os.path.join(self.dir, "*.TXT")
        # la fonction glob permet de lister les fichiers correspondant au pattern
        fichiers = glob(pattern)
        # la fonction map permet d'appliquer à chaque élément d'un itérable (notre liste de fichiers) une même fonction (Datafficheur._load_datafficheur_file)
        # cette fonction renvoie un objet itérable qui permet de lister les retours de la fonction appliqué à chaque élément.
        datas_par_fichier = [self._load_datafficheur_file(fichier) for fichier in fichiers]
        # on concatène dans un même DataFrame les dataframes qu'on a obtenu pour chaque fichier à la ligne précédente.
        concatenated_datas = pd.concat(datas_par_fichier)
        # On trie les valeurs par l'index, qui correspond à l'instant de chaque mesure
        sorted_datas = concatenated_datas.sort_index()
        # On supprime les doublons de l'index
        # Vu avec Deny Fady : parfois la boucle d'écriture est décalée avec la boucle de mesure.
        # On ne conserve qu'une ligne sur les deux écrites dans ce cas.
        self.datas = sorted_datas[~sorted_datas.index.duplicated('first')]

        self.write_output()
        pass

    def _read_row_datetime(self, row):
        """
            Reconstitue le datetime d'une ligne du fichier brut avec la date (colonne 1), l'heure (colonne 2) et la déciseconde (colonne 3)
        """
        return self.timezone.localize(datetime.strptime(
            row[1] + ' ' + row[2] + '.' + str(row[3]),
            '%d/%m/%Y %H:%M:%S.%f'
        ))

    def _load_datafficheur_file(self, fichier: str):
        # On ignore le fichier TEST.TXT
        if fichier.upper().endswith("\\TEST.TXT"):
            return None

        if self.verbose:
            print(f"Traitement du fichier {fichier}")

        # Le nom du fichier correspond à un horodatage, mais on le retrouve aussi dans les lignes du fichiers
        # (_, nom_fichier_complet) = os.path.split(fichier)
        # nom_fichier, _ = os.path.splitext(nom_fichier_complet)
        # mois = nom_fichier[0:2]
        # jour = nom_fichier[2:4]
        # heure = nom_fichier[4:6]
        # minute = nom_fichier[6:8]
        # Lecture du fichier CSV
        datas_fichier = pd.read_csv(
            fichier,
            header=None,
        )
        # Les trois premières colonnes correspondent à l'en-tête (numéro de ligne, date, heure)
        datas_fichier.set_index([0, 1, 2], inplace=True)

        # Pour les colonnes, on va construire un nom à deux niveaux.
        # le premier niveau correspond à la déciseconde ; le deuxième niveau correspond au numéro du capteur (1 ou 2)

        def calcul_nom_colonne(x, frequence_acquisition=10):
            fraction_seconde = x % frequence_acquisition
            numero_capteur = x // frequence_acquisition + 1
            return (fraction_seconde, numero_capteur)

        # Application de la fonction qui calcule les nouveaux noms de colonne, avec deux niveau
        datas_fichier.columns = pd.MultiIndex.from_tuples(map(calcul_nom_colonne, range(len(datas_fichier.columns))))

        # L'appel à stack permet de basculer les colonnes des fractions de seconde en lignes ; tout en conservant une colonne pour chaque capteur.
        datas_fichier = datas_fichier.stack(level=0)
        # On peut alors reconstituer un datetime avec la date (colonne 1), l'heure (colonne 2) et la déciseconde (colonne 3)
        # Ce datetime donne un nouvel index pour les valeurs
        datas_fichier.index = [self._read_row_datetime(row) for row in datas_fichier.index]

        return datas_fichier

    # fonction pour calculer une moyenne sur une fenêtre glissante
    def moving_average(x, w):
        return np.convolve(x, np.ones(w), mode="same") / w

    def write_output(self):

        if self.verbose:
            print(f"Préparation des données {self.datas.index}")

        # le tableau datafficheur.datas contient une colonne pour chaque capteur
        # On va créer un nouveau dataframe, avec des colonnes à deux niveaux.
        # le premier niveau sera alors le capteur ; le deuxième niveau étant pour la première colonne les valeurs, pour la deuxième colonne la moyenne sur 10 valeurs consécutives
        df = {}
        for col in self.datas.columns:
            # je refais une nouvelle dataframe, pour avoir une colonne valeur, une colonne moyenne, et en index la date
            df[col] = pd.DataFrame(
                data={
                    # valeurs brutes
                    "Efforts": self.datas[col],
                    # calcul de la moyenne mobile sur 1s (10 points)
                    # je supprime la ligne d'en dessous pour virer les calculs des moyennes glissantes
                    # "moyenne" : moving_average(datafficheur.datas[col],10), # Modif Deny
                },
                # l'index du dataframe est la date
                index=self.datas.index
            )
            df[col].index.name = "date"
        # concaténation des tableaux de chaque capteur
        df = pd.concat(df, axis=1)

        # calcul des totaux des deux capteurs
        df_total = df.groupby(axis=1, level=1).sum()
        # et on ajoute ça dans le tableau où figurent déjà les données des deux capteurs
        for col in df_total.columns:
            df[("Total", col)] = df_total[col]

        # affichage des données du datafficheur sur une courbe
        if self.plot:
            if self.verbose:
                print("Création du graphique.")
            plt.gca().xaxis_date(self.timezone)
            plt.plot(df, label=df.columns)
            plt.legend()
            if (self.outputplot):
                if self.verbose:
                    print(f"Export du graphique dans {self.outputplot}.")
                plt.savefig(os.path.join(self.dir, self.outputplot))
            else:
                plt.show()

        # Fusion sur un seul niveau des noms de colonnes pour écriture du fichier csv
        df.columns = [' '.join(str(level) for level in col) for col in df.columns]

        # On sépare l'index de type datetime en deux niveaux, date et heure
        df.index = pd.MultiIndex.from_arrays([
            df.index.date,
            [t.strftime("%H:%M:%S.%f")[:10] for t in df.index.time]  # Pour l'heure, je n'affiche que la déci-seconde.
        ], names=['date', 'heure'])

        if self.verbose:
            print(f"Ecriture du fichier de sortie {self.output}")

        df.to_csv(os.path.join(self.dir, self.output))

        if self.verbose:
            print("Traitement terminé.")


Datafficheur()
