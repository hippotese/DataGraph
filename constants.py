DEFAULT_TIMEZONE = "Europe/Paris"

## Fichier de sortie CSV
#OUTPUT = None
OUTPUT = "Kassine_Gaia_01.csv"

## Fichiers de sortie des graphiques
#OUTPUTPLOT = None
OUTPUTPLOT = "Kassine_Gaia_01.pdf"


## Fichiers de sortie des graphiques
#OUTPUTFILE = None
OUTPUTFILE = "Kassine_Gaia_01.png"


## Graphique effort/temps
# Niveau de transparence des courbes:
# Doit etre entre 0 et 1 (exemple 0.5)
# 1 signifie complètement opaque
# 0 signifie complètement transparent
GRAPH_ALPHA = 0.7

## Graphique histograms
# Nombre de subdivisions de l'axe X
# Utile pour rester lisible quand on a de fortes valeurs (plusieurs centaines de kgf)
HISTO_SUBDIVISIONS_X = 20 # defaut
#HISTO_SUBDIVISIONS_X = 10

## Valeur à partir de laquelle on doit exclure les efforts pour le tracé de la courbe de fréquence d'apparition
#EXCLURE = 0 # on garde toutes les valeurs
EXCLURE = 45 # on exclue les valeurs inférieures à 45

## Calcul par densité ou par nombre d'occurences
DENSITY = True # calcul par densité
#DENSITY = False # calcul par nombres d'occurences

## Largeur des barres de l'histogramme des fréquences d'apparition
#BINS = 100 # barres très étroites
#BINS = 60 # barres étroites
BINS = 30 # barres plus larges

