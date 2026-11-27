// Modèles géométriques du système 5 barres — À IMPLÉMENTER.
// Voir include/five_bars_kinematics/kinematics.hpp pour les conventions.

#include "five_bars_kinematics/kinematics.hpp"

namespace five_bars_kinematics
{

std::optional<PenPosition> forwardKinematics(const JointAngles & /*q*/, const Geometry & /*geometry*/)
{
  // TODO : implémenter le modèle géométrique direct.
  return std::nullopt;
}

std::optional<JointAngles> inverseKinematics(const PenPosition & /*p*/, const Geometry & /*geometry*/)
{
  // TODO : implémenter le modèle géométrique inverse.
  return std::nullopt;
}

}  // namespace five_bars_kinematics
