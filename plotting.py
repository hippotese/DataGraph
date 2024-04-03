from matplotlib import pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm
from constants import GRAPH_ALPHA, HISTO_SUBDIVISIONS_X, PLOTHTICKS, DENSITY, BINS, EXCLURE, EXCLURESUP, OUTPUTFILE


def create_plot(df, outputplot=None, verbose=False, hticks=10, sufixe=None, show=True):
    """
    Cree un graphique a partir des donnees fournies et l'enregistre dans un fichier si specifie.

    Args:
        df (pandas.DataFrame): Le DataFrame a representer graphiquement.
        outputplot (str, optional): Le nom du fichier ou sauvegarder le graphique. Si None, le graphique est affiche. Par defaut : None.
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
        raise ValueError("outputplot doit etre une chaine de caracteres.")

    if not show:
        matplotlib.use('Agg')

    #plt.figure(figsize=(19.20, 10.80), dpi=300)    
    #plt.figure(figsize=(19.20, 10.80), dpi=200)
    plt.figure(figsize=(9.60, 5.40), dpi=200)
    #plt.figure(figsize=(19.20, 10.80), dpi=100)
    #plt.figure(figsize=(19.20, 10.80), dpi=50)

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
    plt.ylabel("kgf (kilogramme force - comparable au daN)")

    plt.savefig(outputplot)



###########
###########
#def create_histograms(df, outputfile=None, exclure=9, verbose=False):
def create_histograms(df, outputfile=OUTPUTFILE, exclure=EXCLURE, excluresup=EXCLURESUP, verbose=False, show=True):
    """
    Crée un histogramme et une courbe KDE pour chaque colonne du DataFrame,
    excluant les valeurs inférieures à un certain seuil.
    Chaque colonne est présentée dans un sous-graphique séparé.

    Args:
        df (pandas.DataFrame): Le DataFrame dont les donnees seront utilisees pour les histogrammes.
        outputfile (str): Le nom du fichier ou sauvegarder le graphique.
        exclure (float, optional): Le seuil en dessous duquel les valeurs seront exclues de l'histogramme. Par defaut : 9.
        excluresup (float, optional): Le seuil en dessus duquel les valeurs seront exclues de l'histogramme. Par defaut : 9.

    Returns:
        None

    Raises:
        ValueError: Si df n'est pas un DataFrame pandas.
                    Si outputfile n'est pas une chaîne de caracteres.
                    Si exclure n'est pas un nombre.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df doit être un DataFrame pandas.")
    #if not isinstance(outputfile, str):
    if outputfile is not None and not isinstance(outputfile, str):
        raise ValueError("outputfile doit être une chaîne de caractères.")
    if not isinstance(exclure, (int, float)):
        raise ValueError("exclure doit être un nombre.")


    if not show:
        matplotlib.use('Agg')

    num_cols = len(df.columns)
    fig, axs = plt.subplots(num_cols, figsize=(10, 6 * num_cols))

    # Pour chaque colonne du DataFrame
    for i, column_name in enumerate(df.columns):
        data = df[column_name]
        data = data[data > exclure]  # Exclure les valeurs inférieures
        data = data[data < excluresup]  # Exclure les valeurs inférieures

        # Créer l'histogramme avec des espaces entre les barres (c.f. Note density)
        axs[i].hist(
            #data, bins=30, rwidth=0.9, density=True, alpha=0.3, label=column_name
            ################### densité à la place du nombre d'occurences pour pouvoir comparer différentes mesures
            ###################
            data, bins=BINS, rwidth=0.9, density=DENSITY, alpha=0.3, label=column_name
        )

        # Ajouter une courbe de distribution de noyau (c.f. Note KDE)
        sns.kdeplot(data, bw_adjust=0.5, ax=axs[i])
        
        # Ajouter une courbe de distribution normale
        mu, std = data.mean(), data.std()
        x = np.linspace(data.min(), data.max(), 100)
        p = norm.pdf(x, mu, std)
        axs[i].plot(x, p, "k", linestyle="--", label="Distribution Normale")

        # Ajouter des droites verticales pour la moyenne et l'écart type
        axs[i].axvline(
            mu,
            color="red",
            linestyle="dotted",
            alpha=0.7,
            linewidth=2,
            label=f"Moyenne: {mu:.0f} kgf",
        )
        axs[i].axvline(
            mu - std,
            color="purple",
            linestyle="dotted",
            alpha=0.7,
            linewidth=2,
            label=f"-1 Ec-Typ: {mu-std:.0f} kgf",
        )
        axs[i].axvline(
            mu + std,
            color="green",
            linestyle="dotted",
            alpha=0.7,
            linewidth=2,
            label=f"+1 Ec-Typ: {mu+std:.0f} kgf",
        )

        #axs[i].set_title(f"Histogramme et KDE de {column_name}")
        axs[i].set_title(f"DATAFFICHEUR - Histogramme de fréquence d'apparition des valeurs d'effort pour capt : {column_name}")
        axs[i].legend()

        # Changer les subdivisions de X
        axs[i].xaxis.set_major_locator(plt.MaxNLocator(HISTO_SUBDIVISIONS_X))

        #axs[i].set_xlabel("kgf (kilogramme force - équivalant daN)")
        #axs[i].set_xlabel("kgf (kilogramme force - comparable au daN) \n  \n ")
        axs[i].set_xlabel("kgf (kilogramme force - comparable au daN).   Plage " + str(exclure) + " kgf - " + str(excluresup) + " kgf  \n  \n ")

    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout()



    #if outputfile:
    #if verbose:
    #    print(f"Export du graphique dans {outputfile}.")
    plt.savefig(outputfile)
    #plt.close()  # Ferme la figure pour liberer de la memoire
    #else:

    ### mis en commentaire pour pas afficher 2 fois le graphique à l'écran
    if show:
        plt.show()


# Note density :
#   L'option density dans la fonction hist de matplotlib change l'axe des y de l'histogramme 
#   pour afficher une estimation de la densité de probabilité au lieu du nombre de données dans chaque bin.
#
#   Lorsque density=True, les valeurs de l'histogramme sont normalisées de telle manière que 
#   l'aire sous l'histogramme (c'est-à-dire l'intégrale de la densité de probabilité sur toute la 
#   plage de données) est égale à 1. Cela signifie que chaque barre de l'histogramme n'affiche plus
#   le nombre d'observations dans chaque bin, mais plutôt l'estimation de la densité de 
#   probabilité que la valeur aléatoire tombe dans ce bin.
#
#   Cela permet de comparer des histogrammes de différents ensembles de données qui peuvent avoir des 
#   nombres d'échantillons différents. Il est également utile pour comparer avec une distribution de 
#   probabilité théorique ou pour ajuster une courbe à l'histogramme.
#                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Note KDE :
#   KDE signifie Kernel Density Estimation (Estimation de la densité par noyaux). C'est une technique qui 
#   permet d'estimer la fonction de densité de probabilité (PDF) d'une variable aléatoire. 
#   En termes simples, elle permet de lisser un histogramme.
#
#   Lorsque vous créez un histogramme pour représenter la distribution de vos données, 
#   le nombre de "bins" (c'est-à-dire les barres de l'histogramme) et leur largeur peuvent 
#   avoir un impact important sur l'apparence de l'histogramme. Deux personnes peuvent interpréter 
#   différemment les données en fonction de la façon dont elles choisissent de "biner" ces données. 
#   C'est un des problèmes majeurs des histogrammes.
#
#   L'estimation de densité par noyaux est une technique qui permet de "lisser" un histogramme. 
#   Au lieu de "biner" les données, elle utilise une "fonction de noyau" (d'où le nom "Kernel Density Estimation") 
#   pour créer une courbe lisse qui s'adapte aux données. Cette courbe peut alors être utilisée 
#   pour estimer la densité de probabilité à n'importe quel point.
