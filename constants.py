DEFAULT_TIMEZONE = "Europe/Paris"

## Fichier de sortie CSV
#OUTPUT = None
OUTPUT = "Prob-capt-Uzes.csv"

## Fichiers de sortie des graphiques
#OUTPUTPLOT = None
OUTPUTPLOT = "Prob-capt-Uzes.pdf"


## Fichiers de sortie des graphiques
#OUTPUTFILE = None
OUTPUTFILE = "Prob-capt-Uzes.png"


## Graphique effort/temps
# Niveau de transparence des courbes:
# Doit etre entre 0 et 1 (exemple 0.5)
# 1 signifie complètement opaque
# 0 signifie complètement transparent
GRAPH_ALPHA = 0.7

## Graphique histograms
# Nombre de subdivisions de l'axe X
#HISTO_SUBDIVISIONS_X = 20 # defaut
HISTO_SUBDIVISIONS_X = 10

## Graphique histograms
# Nombre de subdivisions de l'axe Y
# Utile pour rester lisible quand on a de fortes valeurs (plusieurs centaines de kgf)
PLOTHTICKS = 10 #defaut efforts à 70-90 kg
#PLOTHTICKS = 15
#PLOTHTICKS = 20 # quand les efforts sont supèrieurs à 120 kg

## Valeur à partir de laquelle on doit exclure les efforts pour le tracé de la courbe de fréquence d'apparition
EXCLURE = 0 # on garde toutes les valeurs
#EXCLURE = 5
#EXCLURE = 9
#EXCLURE = 15
#EXCLURE = 20
#EXCLURE = 25
#EXCLURE = 35
#EXCLURE = 40
#EXCLURE = 45 # on exclue les valeurs inférieures à 45
#EXCLURE = 50

## Valeur au dela desquelle on doit exclure les efforts pour le tracé de la courbe de fréquence d'apparition
#EXCLURESUP = 5
#EXCLURESUP = 45
#EXCLURESUP = 100 #
EXCLURESUP = 1000 # on garde toutes les valeurs

## Calcul par densité ou par nombre d'occurences
DENSITY = True # calcul par densité
#DENSITY = False # calcul par nombres d'occurences

## Largeur des barres de l'histogramme des fréquences d'apparition
#BINS = 100 # barres très étroites
#BINS = 60 # barres étroites
BINS = 50
#BINS = 30 # barres plus larges

