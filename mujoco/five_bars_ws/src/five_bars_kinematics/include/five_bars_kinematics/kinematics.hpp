// Modèles géométriques DIRECT et INVERSE du système 5 barres — À IMPLÉMENTER
// dans src/kinematics.cpp.
//
// Les tests test/test_kinematics.cpp (Google Test) comparent ces fonctions à la
// simulation MuJoCo (headless). Ils ÉCHOUENT tant que les fonctions ne sont pas implémentées.
//
// Conventions (schéma cinématique du cours, repère R0) :
//   * A1 = (0, 0) : axe du moteur gauche ; A5 = (l0, 0) : axe du moteur droit ;
//   * q1 : angle ABSOLU (par rapport à x0) du bras gauche A1A2  (|A1A2| = l1) ;
//   * q4 : angle ABSOLU (par rapport à x0) du bras droit  A5A4  (|A5A4| = l4) ;
//   * avant-bras gauche A2A3 (l2), avant-bras droit A4A3 (l3), fermés en A3 ;
//   * le stylo est fixé sur l'avant-bras gauche (link2), DÉCALÉ par rapport à A3 :
//         P = A3 + pen_dx * u2 + pen_dy * v2
//     avec u2 = (A3 - A2) / l2 et v2 = u2 tourné de +90° (à gauche de A2->A3) ;
//   * longueurs en mètres, angles en radians.
//
// Mode d'assemblage attendu (celui du robot, du schéma et de la simulation) :
//   * modèle direct : A3 est à GAUCHE du vecteur A2->A4 ;
//   * modèle inverse : A2 est à GAUCHE du vecteur A1->P et A4 à DROITE du vecteur A5->A3.

#ifndef FIVE_BARS_KINEMATICS__KINEMATICS_HPP_
#define FIVE_BARS_KINEMATICS__KINEMATICS_HPP_

#include <optional>

namespace five_bars_kinematics
{

/// Paramètres géométriques (m). Voir five_bars_description/config/geometry.yaml.
struct Geometry
{
  double l0;      ///< |A1A5|
  double l1;      ///< |A1A2|
  double l2;      ///< |A2A3|
  double l3;      ///< |A4A3|
  double l4;      ///< |A5A4|
  double pen_dx;  ///< décalage du stylo par rapport à A3, le long de A2->A3
  double pen_dy;  ///< décalage du stylo par rapport à A3, à gauche de A2->A3
};

/// Angles absolus des deux moteurs (rad).
struct JointAngles
{
  double q1;
  double q4;
};

/// Position de la pointe du stylo dans R0 (m).
struct PenPosition
{
  double x;
  double y;
};

/// Modèle géométrique direct : (q1, q4) -> (x, y) du stylo.
/// @return std::nullopt si la chaîne ne peut pas se fermer pour ces angles.
std::optional<PenPosition> forwardKinematics(const JointAngles & q, const Geometry & geometry);

/// Modèle géométrique inverse : (x, y) du stylo -> (q1, q4), angles dans ]-pi, pi].
/// @return std::nullopt si le point n'est pas atteignable.
std::optional<JointAngles> inverseKinematics(const PenPosition & p, const Geometry & geometry);

}  // namespace five_bars_kinematics

#endif  // FIVE_BARS_KINEMATICS__KINEMATICS_HPP_
