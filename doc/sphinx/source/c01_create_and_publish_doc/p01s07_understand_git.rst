************************************** 
Pour aller plus loin : Comprendre git
**************************************

.. index:: git

Git fonctionne en enregistrant les différences entre les versions d'un fichier. 
Pour cela il utilise un système de points de contrôle appelés commits. 
Un commit est un point de contrôle qui enregistre l'état des fichiers à un instant donné. Il est possible de revenir à un commit précédent à tout moment.
Ce qui est fondamental à comprendre c'est que git ne stocke pas les fichiers mais les différences entre les fichiers.

=========================================================================
Comment git calcule les différences entre 2 versions d'un même fichier ?
=========================================================================

Git utilise un algorithme de différences pour calculer les différences entre 2 versions d'un fichier. 

L'utilitaire de ligne de commande ``diff`` permet de calculer et de visualiser les différences entre 2 fichiers.
Sous linux, vous pouvez l'utiliser en ligne de commande de la manière suivante :

.. code-block:: bash

   diff fichier1 fichier2

Il produit un affichage de la différence entre les 2 fichiers.

-------------------------------------------------------------
Les outils pour visualiser les différences entre 2 fichiers
-------------------------------------------------------------

^^^^^^^
vscode
^^^^^^^
Dans vscode vous pouvez visualiser les différences entre 2 fichiers en utilisant pour les 2 versions d'un même fichier ``Select for Compare`` qui s'obtient en faisant un clic droit sur chaque version du fichier dans l'explorateur de fichiers.


^^^^^^^^
Kompare
^^^^^^^^

Kompare est un outil graphique pour visualiser les différences entre 2 fichiers, très bien fait qui fait partie de la suite kde.
Il s'installe avec la commande suivante :

.. code-block:: bash

   sudo apt-get install kompare

Il s'utilise en ligne de commande de la manière suivante :

.. code-block:: bash

   kompare fichier1 fichier2


===============================================================
Implications de l'utilisation de git dans la rédaction de code
===============================================================

L'unité de base étant la ligne, il est important de placer sur des lignes différentes des éléments dont la sémantique est différente.
Ainsi pour un fichier comme ce cours (c'est aussi valable pour un rapport ou une thèse), il est très intéressant de placer des phrases différentes sur des lignes différentes.
On laisse le soin au système de mise en forme de texte de gérer les retours à la ligne.
C'est naturellement ce qui se passe avec LaTex (.tex) ou restructuredtext (.rst), ce dernier étant le format utilisé par ce cours pour générer cette documentation avec sphinx.


====================================================
Pour aller plus loin sur l'algorithme de différence
====================================================

L'algorithme est appelé algorithme de différences en ligne de Myers. 
Il cherche les plus longues sous-séquence de lignes communes entre les 2 fichiers.
Des bonnes explications sont disponibles:

* James Coglan présente un article sur son blog en 2 parties: 

   * `The Myers diff algorithm: part 1 <http://blog.jcoglan.com/2017/09/19/the-myers-diff-algorithm-part-1/>`_.
   * `The Myers diff algorithm: part 2 <http://blog.jcoglan.com/2017/09/19/the-myers-diff-algorithm-part-2/>`_.

* Nicholas Butler présente un bon article sur son blog: 

   * `Myers' Diff Algorithm: The basic greedy algorithm <http://simplygenius.net/Article/DiffTutorial1>`_.
   * `Myers' Diff Algorithm : The linear space refinement <http://simplygenius.net/Article/DiffTutorial2>`_.


* `Wikipedia Diff article <https://en.wikipedia.org/wiki/Diff>`_.


===========================================
Comment versionner les fichiers binaires ?
===========================================


.. index::
   git; fichiers binaires
   git; lfs
   git lfs
   modèles d'IA; versionnement

Tout ce qui précède repose sur une hypothèse : le fichier est un **fichier texte**, découpable en lignes.
Or un projet de robotique contient beaucoup de fichiers qui ne sont pas du texte : des maillages 3D (``.stl``, ``.dae``), des images et des vidéos, des enregistrements de bags ROS 2 (``.mcap``, ``.db3``) et, de plus en plus souvent, des **modèles d'intelligence artificielle** (les poids d'un réseau de neurones).

--------------------------------------------------------------
Pourquoi git est-il en difficulté avec les fichiers binaires ?
--------------------------------------------------------------

Un fichier binaire n'a pas de lignes : l'algorithme de Myers n'a donc rien à comparer.
Git est alors obligé de conserver **chaque version du fichier dans son intégralité**.
Pire, la plupart des formats binaires sont compressés (un ``.pt`` PyTorch est une archive zip, un ``.jpg`` est compressé) : changer un seul paramètre du modèle modifie la quasi-totalité des octets du fichier.
Trois conséquences très concrètes :

#. **Le dépôt grossit sans limite** : 10 versions d'un modèle de 200 Mo, c'est 2 Go dans l'historique, et cet historique est recopié intégralement à chaque ``git clone``, pour toujours (même si vous supprimez le fichier ensuite).
#. **Les différences sont illisibles** : ``git diff`` affiche seulement ``Binary files a/model.onnx and b/model.onnx differ``.
#. **Les conflits sont infusionnables** : si deux personnes modifient le même binaire, git ne peut pas fusionner, il faut choisir une version et perdre l'autre.

.. note:: Les plateformes en ligne imposent de plus des limites par fichier : GitHub refuse les fichiers de plus de 100 Mo lors d'un ``git push`` et avertit au-delà de 50 Mo. Un modèle d'IA dépasse très vite ce seuil.

-----------------------------------------------------------------
Git LFS : garder les gros fichiers en dehors de l'historique
-----------------------------------------------------------------

**Git LFS** (*Large File Storage*, stockage des gros fichiers) est une extension de git qui résout ce problème par une indirection.
Au moment du commit, le fichier binaire est remplacé dans le dépôt par un petit **fichier texte de quelques centaines d'octets**, appelé *pointeur*, qui contient l'empreinte (``sha256``) et la taille du vrai fichier :

.. code-block:: text

   version https://git-lfs.github.com/spec/v1
   oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
   size 131613504

Ce pointeur, lui, est du texte : git le versionne, le compare et le fusionne parfaitement.
Le fichier réel est envoyé en parallèle sur un **serveur LFS** (celui de GitHub, GitLab, Hugging Face ou le vôtre) et n'est redescendu sur votre machine que pour la version que vous avez extraite.
L'historique du dépôt reste donc léger, et ``git clone`` reste rapide.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Exemple typique : les modèles d'intelligence artificielle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Les poids d'un réseau de neurones sont le cas d'école du fichier binaire volumineux, régulièrement remplacé (ré-entraînement, nouveau jeu de données, quantification) et impossible à fusionner.

.. list-table:: Formats de modèles d'IA couramment rencontrés en robotique
   :header-rows: 1
   :align: center
   :widths: 20 40 40

   * - Extension
     - Contenu
     - Exemples et ordres de grandeur
   * - ``.pt`` / ``.pth``
     - Poids PyTorch
     - ``yolov8n.pt`` (≈ 6 Mo), ``yolov8x.pt`` (≈ 130 Mo)
   * - ``.safetensors``
     - Poids Hugging Face (format sûr)
     - modèles de vision ou de langage, de 100 Mo à plusieurs Go
   * - ``.onnx``
     - Modèle échangeable entre frameworks
     - ``resnet50.onnx`` (≈ 100 Mo)
   * - ``.engine`` / ``.plan``
     - Moteur TensorRT compilé pour un GPU
     - généré sur la cible (Jetson), **à ne pas versionner**
   * - ``.tflite``
     - Modèle embarqué quantifié
     - ``mobilenet_v2.tflite`` (≈ 14 Mo)
   * - ``.gguf``
     - Modèle de langage quantifié (llama.cpp)
     - de 1 à 40 Go selon la quantification

.. note:: Le site **Hugging Face** est lui-même un ensemble de dépôts git utilisant Git LFS : lorsque vous faites ``git clone https://huggingface.co/...``, ce sont les pointeurs LFS qui sont clonés, puis les poids qui sont téléchargés. C'est exactement le mécanisme décrit ici.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Installer git lfs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sous Ubuntu (ou sous WSL) :

.. code-block:: bash

   sudo apt-get update && sudo apt-get install git-lfs

Puis, **une seule fois par compte utilisateur**, pour installer les filtres dans votre configuration git globale :

.. code-block:: bash

   git lfs install

Vérifiez l'installation :

.. code-block:: bash

   git lfs version

.. note:: Sous macOS : ``brew install git-lfs``. Sous Windows, Git LFS est fourni avec *Git for Windows* ; si vous suivez ce cours sous WSL, utilisez la commande ``apt-get`` ci-dessus à l'intérieur de WSL.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Placer des fichiers sous Git LFS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On déclare les **motifs de fichiers** à suivre, et non les fichiers un par un :

.. code-block:: bash

   cd ~/info_indus/info_indus_tutorial
   git lfs track "*.pt"
   git lfs track "*.onnx"
   git lfs track "*.safetensors"
   git lfs track "models/**"

Ces commandes ne font qu'écrire dans un fichier ``.gitattributes`` à la racine du dépôt :

.. code-block:: text

   *.pt filter=lfs diff=lfs merge=lfs -text
   *.onnx filter=lfs diff=lfs merge=lfs -text

Ce fichier **doit impérativement être versionné et poussé en premier**, sinon vos collègues (et la CI) committeront les binaires en clair :

.. code-block:: bash

   git add .gitattributes
   git commit -m "[lfs] Suivi des modeles d'IA avec git lfs"

Ensuite, le fichier binaire s'ajoute comme n'importe quel autre fichier :

.. code-block:: bash

   git add models/yolov8x.pt
   git commit -m "[model] Ajout du modele de detection yolov8x"
   git push

Pour contrôler ce qui est réellement géré par LFS :

.. code-block:: bash

   git lfs ls-files
   git lfs status

.. warning:: ``git lfs track`` n'agit que sur les fichiers ajoutés **après** la déclaration. Un fichier déjà présent dans l'historique y reste : il faut réécrire l'historique (voir la migration ci-dessous). Déclarez donc vos motifs LFS **dès la création du dépôt**.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Récupérer un dépôt qui contient des fichiers LFS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Si ``git lfs`` est installé, le fonctionnement est transparent : ``git clone`` et ``git pull`` téléchargent les vrais fichiers.
Si vous récupérez un dépôt et que vous ne trouvez que des pointeurs (un fichier ``.onnx`` de 130 octets), c'est que LFS n'était pas installé : corrigez-le avec

.. code-block:: bash

   git lfs install && git lfs pull

Pour cloner **sans** télécharger les gigaoctets de poids (très utile pour inspecter un dépôt de modèles) :

.. code-block:: bash

   GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/openai/whisper-small

puis télécharger seulement ce dont vous avez besoin :

.. code-block:: bash

   git lfs pull --include="*.safetensors"

Enfin, pour faire du ménage dans le cache local des anciennes versions :

.. code-block:: bash

   git lfs prune

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Migrer un dépôt existant vers LFS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pour savoir quels types de fichiers pèsent lourd dans votre historique :

.. code-block:: bash

   git lfs migrate info --everything --above=10Mb

Puis pour déplacer rétroactivement ces fichiers dans LFS :

.. code-block:: bash

   git lfs migrate import --everything --include="*.pt,*.onnx"

.. warning:: ``git lfs migrate import`` **réécrit l'historique** : tous les identifiants de commits changent. Il faut donc pousser en force (``git push --force-with-lease``) et prévenir **tous** les collaborateurs, qui devront recloner le dépôt. À ne faire que sur un dépôt dont on maîtrise les utilisateurs, et jamais pendant qu'une pull request est en cours.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Verrouiller un fichier que l'on ne peut pas fusionner
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Comme deux modifications concurrentes d'un binaire sont infusionnables, LFS propose un verrou explicite, qui prévient les autres que le fichier est en cours de modification :

.. code-block:: bash

   git lfs lock models/yolov8x.pt
   git lfs locks
   git lfs unlock models/yolov8x.pt

On peut rendre ce verrou obligatoire en déclarant le motif ``lockable`` dans ``.gitattributes`` (les fichiers sont alors en lecture seule tant qu'ils ne sont pas verrouillés) :

.. code-block:: text

   *.pt filter=lfs diff=lfs merge=lfs -text lockable

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Attention aux quotas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le stockage LFS n'est pas gratuit et illimité : sur GitHub, l'offre gratuite se compte en **quelques gigaoctets de stockage et de bande passante par mois** (vérifiez les conditions en vigueur, elles évoluent), et la bande passante est consommée à **chaque** clonage, y compris par la CI.
Un dépôt de cours cloné par 50 étudiants avec un modèle de 500 Mo épuise le quota en une séance.
Alternatives courantes :

* héberger les modèles sur **Hugging Face Hub**, conçu pour cela, et ne versionner dans le dépôt de code que l'identifiant du modèle ;
* attacher les gros fichiers à une **release** GitHub (hors LFS) ;
* utiliser un outil dédié aux données et modèles comme **DVC**, qui applique le même principe de pointeur mais avec un stockage de votre choix (S3, serveur de laboratoire, disque réseau) ;
* ne rien stocker du tout et **télécharger le modèle à la demande** depuis un script, en vérifiant son empreinte ``sha256``.

-------------------------------------------------------------
Les bonnes pratiques pour versionner des fichiers binaires
-------------------------------------------------------------

#. **Préférer un format texte chaque fois qu'il existe.** Un ``.urdf``/``.xacro``, un ``.csv``, un ``.json``, un ``.svg`` ou un fichier de configuration ``.yaml`` se comparent et se fusionnent ; leur équivalent binaire, non. C'est un critère de choix de format à part entière.
#. **Ne jamais versionner ce qui est généré.** Un moteur TensorRT ``.engine``, un ``build/``, un ``install/``, un ``__pycache__`` ou une vidéo de démonstration ré-encodée se régénèrent : ils vont dans le ``.gitignore``, pas dans LFS.
#. **Ne versionner que les binaires qui sont des sources**, c'est-à-dire ceux que l'on ne sait pas reconstruire : poids d'un modèle entraîné, maillage de CAO, image de référence pour un test.
#. **Accompagner chaque binaire d'un fichier texte de métadonnées** versionné à côté de lui (par exemple ``yolov8x.md`` ou ``models.yaml``) : provenance, licence, date, empreinte ``sha256``, jeu de données et script d'entraînement, performances mesurées. C'est ce fichier texte, lui, qui portera l'historique lisible des évolutions.
#. **Committer un binaire seul, dans un commit dédié**, avec un message explicite : cela permet de repérer et, si besoin, d'annuler facilement les commits lourds.
#. **Étiqueter les versions** (``git tag``) qui correspondent à un modèle livré, pour pouvoir retrouver exactement le couple code + modèle utilisé lors d'une démonstration ou d'une publication.
#. **Mettre en place LFS dès le premier commit** du dépôt : c'est le seul moyen d'éviter une réécriture d'historique douloureuse.
