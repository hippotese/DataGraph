from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from constants import GRAPH_ALPHA


def create_plot(df, outputplot=None, verbose=False, hticks=10, sufixe=None):
    """
    Cree un graphique e partir des donnees fournies et l'enregistre dans un fichier si specifie.

    Args:
        df (pandas.DataFrame): Le DataFrame e representer graphiquement.
        outputplot (str, optional): Le nom du fichier oe sauvegarder le graphique. Si None, le graphique est affiche. Par defaut : None.
        verbose (bool, optional): Si vrai, affiche des messages supplementaires pendant la creation du graphique. Par defaut : False.

    Returns:
        None

    Raises:
        ValueError: Si df n'est pas un DataFrame pandas 
                    Si outputplot n'est pas une chaine de caracteres
                    Si df n'a pas deux ou trois colonnes
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df doit etre un DataFrame pandas.")
    if outputplot is not None and not isinstance(outputplot, str):
        raise ValueError("outputplot doit etre une chaene de caracteres.")

    plt.figure(figsize=(19.20, 10.80), dpi=200)

    plt.gca().xaxis_date()

    # Définition des noms des courbes
    if len(df.columns) == 2:
        labels = ["Capt 1", "Tot"]
    elif len(df.columns) == 3:
        labels = ["Capt 1", "Capt 2", "Tot"]
    else:
        raise ValueError("Le DataFrame doit avoir deux ou trois colonnes.")

    for col, label in zip(df.columns, labels):
        plt.plot(df[col], label=label, alpha=GRAPH_ALPHA)

    max_y = df.max().max()  # Obtient la valeur maximale dans le DataFrame
    plt.yticks(
        np.arange(0, max_y, hticks)
    )  # Definit les ticks de l'axe des y (default 10)
    plt.grid(
        axis="y", linestyle="dotted"
    )  # Dessine une grille horizontale en pointilles

    plt.legend()
    if sufixe == None:
        plt.title("DATAFFICHEUR - Effort en fonction du temps")
    else:
        plt.title("DATAFFICHEUR - Effort en fonction du temps - " + sufixe)
    plt.xlabel("Temps")
    plt.ylabel("kgf (kilogramme force - equivalant daN)")
    if outputplot:
        if verbose:
            print(f"Export du graphique dans {outputplot}.")
        plt.savefig(outputplot)
        plt.close()  # Ferme la figure pour liberer de la memoire
    else:
        plt.show()
