# Datafficheur

Ce programme permet la lecture des données du capteur Datafficheur (http://hippotese.free.fr/blog/index.php/?q=datafficheur).

Il permet :
* l'assemblage des fichiers bruts et la production d'un fichier globale (avec une ligne par dixième de seconde)
* la génération d'un graphique 

Les trames pour 1 capteur
```csv
565,06/10/2022,15:52:11,53,55,69,70,55,56,52,57,63,64 (1 capteur) à
```
sont converties
```csv
06-10-2022,15:52:11.1,53,53
06-10-2022,15:52:11.2,55,55
```

Les trames pour 2 capteurs
```csv
565,06/10/2022,15:52:11,53,55,69,70,55,56,52,57,63,64,52,56,50,50,52,56,61,48,49,39 (2 
```
sont converties
```csv
06-10-2022,15:52:11.1,53,52,105
06-10-2022,15:52:11.2,55,56,111
```

### Usage


```shell
python3 datafficheur.py --help
usage: Datafficheur [-h] [-d DIR] [-v VERBOSE] [-o OUTPUT] [-p PLOT] [-op OUTPUTPLOT] [-z TIMEZONE]

Lecture des données du capteur Datafficheur. http://hippotese.free.fr/blog/index.php/?q=datafficheur

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Chemin vers le dossier contenant les données Datafficheur.
  -v VERBOSE, --verbose VERBOSE
                        Affiche des messages sur la progression.
  -o OUTPUT, --output OUTPUT
                        Nom du fichier créé. Par défaut: output.csv
  -p PLOT, --plot PLOT  Création d un graphique. Par défaut: True
  -op OUTPUTPLOT, --outputplot OUTPUTPLOT
                        Sauvegarde du graphique au format PDF. Par défaut: None
  -z TIMEZONE, --timezone TIMEZONE
                        Fuseau horaire. Par défaut: Europe/Paris
```


### Auteurs

* BPasquiet - 16/06/2022
* Deny Fady
* François Prunayre