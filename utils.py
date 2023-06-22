import re
import os
from datetime import datetime


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
