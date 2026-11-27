"""Modèles géométriques DIRECT et INVERSE du système 5 barres — À IMPLÉMENTER.

Les tests test/test_kinematics.py comparent ces fonctions à la simulation MuJoCo
(headless). Ils ÉCHOUENT tant que les fonctions ne sont pas implémentées.

Conventions (schéma cinématique du cours, repère R0) :
  * A1 = (0, 0) : axe du moteur gauche ; A5 = (l0, 0) : axe du moteur droit ;
  * q1 : angle ABSOLU (par rapport à x0) du bras gauche A1A2  (|A1A2| = l1) ;
  * q4 : angle ABSOLU (par rapport à x0) du bras droit  A5A4  (|A5A4| = l4) ;
  * avant-bras gauche A2A3 (l2), avant-bras droit A4A3 (l3), fermés en A3 ;
  * le stylo est fixé sur l'avant-bras gauche (link2), DÉCALÉ par rapport à A3 :
        P = A3 + pen_dx * u2 + pen_dy * v2
    avec u2 = (A3 - A2) / l2 et v2 = u2 tourné de +90° (vers la gauche de A2->A3).
  * toutes les longueurs en mètres, les angles en radians.

Mode d'assemblage attendu (celui du robot, du schéma et de la simulation) :
  * modèle direct : A3 est à GAUCHE du vecteur A2->A4 (le coude A3 "vers le haut",
    loin du bâti) ;
  * modèle inverse : A2 est à GAUCHE du vecteur A1->P (bras gauche "coude à gauche")
    et A4 est à DROITE du vecteur A5->A3 (bras droit "coude à droite").
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Geometry:
    """Paramètres géométriques (m). Voir five_bars_description/config/geometry.yaml."""

    l0: float
    l1: float
    l2: float
    l3: float
    l4: float
    pen_dx: float
    pen_dy: float


def forward_kinematics(q1: float, q4: float, geometry: Geometry) -> Optional[Tuple[float, float]]:
    """Modèle géométrique direct.

    :param q1: angle absolu du bras gauche (rad)
    :param q4: angle absolu du bras droit (rad)
    :param geometry: paramètres géométriques
    :return: (x, y) de la pointe du stylo dans R0 (m), ou None si la chaîne ne
             peut pas se fermer pour ces angles (|A2A4| > l2 + l3 ou < |l2 - l3|).
    """
    # TODO : implémenter le modèle géométrique direct.
    raise NotImplementedError("forward_kinematics n'est pas encore implémenté")


def inverse_kinematics(x: float, y: float, geometry: Geometry) -> Optional[Tuple[float, float]]:
    """Modèle géométrique inverse.

    :param x: abscisse de la pointe du stylo dans R0 (m)
    :param y: ordonnée de la pointe du stylo dans R0 (m)
    :param geometry: paramètres géométriques
    :return: (q1, q4) en rad, dans ]-pi, pi], ou None si le point n'est pas atteignable.

    Indice : le stylo étant rigidement lié à link2, la chaîne A1 -> A2 -> P est un
    bras plan à 2 segments de longueurs l1 et |A2P|. Une fois A2 trouvé, on en déduit
    A3, puis A4 (et q4) par la chaîne droite A5 -> A4 -> A3.
    """
    # TODO : implémenter le modèle géométrique inverse.
    raise NotImplementedError("inverse_kinematics n'est pas encore implémenté")
