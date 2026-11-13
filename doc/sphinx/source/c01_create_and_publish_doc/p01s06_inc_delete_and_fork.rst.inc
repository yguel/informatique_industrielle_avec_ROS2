.. Ce fichier est inclus DEUX fois dans p01s06_cooperate_by_pull_request.rst :
   une fois dans l'onglet « membre », une fois dans l'onglet « responsable ».
   Ces deux étapes sont en effet rigoureusement identiques pour tout le monde.
   Ne pas y mettre de titre de section ni de cible (.. _label:) : cela créerait
   des doublons. Les chemins d'images sont relatifs au document qui inclut ce
   fichier, c'est-à-dire à c01_create_and_publish_doc/.

.. rubric:: Supprimer votre propre dépôt info_indus_tutorial sur github

Votre dépôt personnel n'est plus la référence : la référence est désormais le dépôt de l'organisation du groupe, et vous allez travailler dans un fork de ce dépôt, qui portera **le même nom** que votre dépôt actuel. Pour qu'aucune confusion ne soit possible entre les deux, nous supprimons votre dépôt personnel.

.. warning::

   La suppression d'un dépôt sur github est **définitive et irréversible**. Elle supprime aussi les branches (dont ``gh-pages``), les actions et la documentation publiée sur le web. Avant de valider, vérifiez deux choses : que le dépôt principal du groupe existe bien dans l'organisation, et que vous êtes bien sur **votre** dépôt personnel ``info_indus_tutorial``.

Procédure :

#. allez sur la page de votre dépôt ``info_indus_tutorial`` sur github ;
#. cliquez sur l'onglet ``Settings`` (en haut, à droite de la liste des onglets) ;
#. restez dans la sous-section ``General`` et descendez tout en bas de la page, jusqu'à l'encadré rouge ``Danger Zone`` ;
#. cliquez sur le bouton ``Delete this repository`` ;
#. github vous demande de confirmer : cochez les cases proposées puis recopiez **exactement** le nom complet du dépôt demandé, de la forme ``mon_login/info_indus_tutorial`` ;
#. cliquez sur le bouton rouge de confirmation ``I understand the consequences, delete this repository``.

   .. figure:: resources/img/pull_request/delete_github_project.gif
      :align: center
      :width: 80%

Mettez aussi de côté votre copie locale, nous allons en récupérer une neuve juste après :

.. code-block:: bash

   mv ~/info_indus/info_indus_tutorial ~/info_indus/info_indus_tutorial_old

.. rubric:: Forker le dépôt principal du groupe

Le dépôt principal est celui de l'organisation ; son adresse est de la forme ``https://github.com/mon_groupe/info_indus_tutorial``.

#. ouvrez cette adresse dans votre navigateur, en étant connecté à votre **compte github personnel** ;
#. cliquez sur le bouton ``Fork``, en haut à droite de la page ;
#. dans la page ``Create a new fork``, laissez le champ ``Owner`` sur **votre login personnel** et le champ ``Repository name`` sur ``info_indus_tutorial`` ;
#. **décochez** la case ``Copy the rolling branch only`` : nous voulons aussi récupérer la branche ``gh-pages`` ;
#. cliquez sur le bouton ``Create fork``.

Vous arrivez sur la page de votre fork. Sous son titre, github affiche ``forked from mon_groupe/info_indus_tutorial`` : c'est la marque du lien entre les deux dépôts, et c'est ce lien qui rendra la pull request possible.

   .. figure:: resources/img/pull_request/create_fork_on_github.gif
      :align: center
      :width: 80%
