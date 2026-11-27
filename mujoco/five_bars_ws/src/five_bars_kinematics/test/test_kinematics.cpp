// Tests unitaires (Google Test) des modèles géométriques direct/inverse du 5 barres.
//
// La vérité terrain est fournie par la simulation MuJoCo HEADLESS (voir mujoco_five_bars.hpp).
// Ces tests ÉCHOUENT tant que src/kinematics.cpp n'est pas implémenté ; seuls les
// tests "SimulationHarness.*" (qui valident le banc de test) passent.
//
//   colcon test --packages-select five_bars_kinematics && colcon test-result --verbose
//   # ou : ./build/five_bars_kinematics/test_kinematics_cpp --gtest_color=yes

#include <gtest/gtest.h>

#include <cmath>
#include <memory>
#include <tuple>
#include <vector>

#include "five_bars_kinematics/kinematics.hpp"
#include "mujoco_five_bars.hpp"

using five_bars_kinematics::forwardKinematics;
using five_bars_kinematics::Geometry;
using five_bars_kinematics::inverseKinematics;
using five_bars_kinematics::JointAngles;
using five_bars_kinematics::PenPosition;
using five_bars_test::MujocoFiveBars;

namespace
{
constexpr double kPosTol = 1e-4;     // 0.1 mm entre modèle et simulation
constexpr double kAngleTol = 1e-3;   // rad
constexpr double kReachTol = 5e-4;   // 0.5 mm après asservissement simulé

double deg(double d) {return d * M_PI / 180.0;}
double wrap(double a) {return std::atan2(std::sin(a), std::cos(a));}

// Configurations de test (degrés) : mode d'assemblage du robot, loin des singularités.
std::vector<std::tuple<double, double>> jointGrid()
{
  std::vector<std::tuple<double, double>> g;
  for (double q1 : {90.0, 110.0, 130.0, 150.0}) {
    for (double q4 : {20.0, 40.0, 60.0, 80.0}) {
      g.emplace_back(q1, q4);
    }
  }
  return g;
}

// Zone de dessin (m).
std::vector<PenPosition> xyTargets()
{
  std::vector<PenPosition> t;
  for (double x : {0.02, 0.04, 0.06, 0.08}) {
    for (double y : {0.13, 0.15, 0.17}) {
      t.push_back({x, y});
    }
  }
  return t;
}
}  // namespace

// Une simulation partagée par toute la suite (chargement du MJCF une seule fois).
class MujocoFixture : public ::testing::Test
{
protected:
  static void SetUpTestSuite() {sim_ = std::make_unique<MujocoFiveBars>();}
  static void TearDownTestSuite() {sim_.reset();}

  void SetUp() override
  {
    sim_->reset();
    geometry_ = sim_->geometry();
  }

  /// Asservit (q1, q4) depuis 'home' ; renvoie les angles mesurés et la position du stylo.
  std::pair<JointAngles, PenPosition> simulate(double q1, double q4)
  {
    sim_->reset();
    EXPECT_TRUE(sim_->settle(q1, q4)) << "la simulation n'a pas convergé";
    EXPECT_LT(sim_->closureError(), 1e-6) << "chaîne non fermée dans la simulation";
    return {sim_->measuredAngles(), sim_->penPosition()};
  }

  static std::unique_ptr<MujocoFiveBars> sim_;
  Geometry geometry_{};
};
std::unique_ptr<MujocoFiveBars> MujocoFixture::sim_;

// ------------------------------------------------------------- banc de test (passe)
using SimulationHarness = MujocoFixture;

TEST_F(SimulationHarness, HomePenPositionMatchesCad)
{
  const auto pen = sim_->penPosition();
  EXPECT_NEAR(pen.x, 0.07345, 1e-3);
  EXPECT_NEAR(pen.y, 0.20220, 1e-3);
}

TEST_F(SimulationHarness, SimulationTracksCommands)
{
  const auto [q, pen] = simulate(deg(120), deg(50));
  (void)pen;
  EXPECT_NEAR(q.q1, deg(120), 1e-4);
  EXPECT_NEAR(q.q4, deg(50), 1e-4);
}

// --------------------------------------------------------------- modèle direct
using ForwardKinematics = MujocoFixture;

TEST_F(ForwardKinematics, HomeConfiguration)
{
  const auto q = sim_->measuredAngles();
  const auto pen = sim_->penPosition();
  const auto p = forwardKinematics(q, geometry_);
  ASSERT_TRUE(p.has_value()) << "forwardKinematics n'a pas renvoyé de solution";
  EXPECT_NEAR(p->x, pen.x, kPosTol);
  EXPECT_NEAR(p->y, pen.y, kPosTol);
}

TEST_F(ForwardKinematics, MatchesMujocoSimulation)
{
  for (const auto & [q1d, q4d] : jointGrid()) {
    SCOPED_TRACE(testing::Message() << "q1=" << q1d << "° q4=" << q4d << "°");
    const auto [q, pen] = simulate(deg(q1d), deg(q4d));
    const auto p = forwardKinematics(q, geometry_);
    ASSERT_TRUE(p.has_value()) << "configuration atteignable déclarée impossible";
    EXPECT_NEAR(p->x, pen.x, kPosTol);
    EXPECT_NEAR(p->y, pen.y, kPosTol);
  }
}

TEST_F(ForwardKinematics, PenOffsetIsTakenIntoAccount)
{
  // Le stylo n'est PAS en A3 : un modèle qui l'oublie doit échouer ici.
  const auto p = forwardKinematics(sim_->measuredAngles(), geometry_);
  ASSERT_TRUE(p.has_value());
  const auto a3 = sim_->siteXY("A3_link2");
  EXPECT_NEAR(
    std::hypot(p->x - a3[0], p->y - a3[1]), std::hypot(geometry_.pen_dx, geometry_.pen_dy), kPosTol);
}

TEST_F(ForwardKinematics, UnassemblableConfigurationReturnsNullopt)
{
  EXPECT_TRUE(forwardKinematics({deg(110), deg(60)}, geometry_).has_value());
  // Bras croisés : |A2A4| < |l2 - l3|, la chaîne ne peut pas se fermer.
  EXPECT_FALSE(forwardKinematics({deg(30), deg(150)}, geometry_).has_value());
}

// --------------------------------------------------------------- modèle inverse
using InverseKinematics = MujocoFixture;

TEST_F(InverseKinematics, MatchesMujocoSimulation)
{
  for (const auto & [q1d, q4d] : jointGrid()) {
    SCOPED_TRACE(testing::Message() << "q1=" << q1d << "° q4=" << q4d << "°");
    const auto [q, pen] = simulate(deg(q1d), deg(q4d));
    const auto r = inverseKinematics(pen, geometry_);
    ASSERT_TRUE(r.has_value()) << "point atteignable déclaré inatteignable";
    EXPECT_NEAR(wrap(r->q1 - q.q1), 0.0, kAngleTol);
    EXPECT_NEAR(wrap(r->q4 - q.q4), 0.0, kAngleTol);
  }
}

TEST_F(InverseKinematics, ReachesTargetsInSimulation)
{
  // IK -> consignes des servos simulés -> le stylo doit arriver sur la cible.
  for (const auto & target : xyTargets()) {
    SCOPED_TRACE(testing::Message() << "cible x=" << target.x << " y=" << target.y);
    const auto r = inverseKinematics(target, geometry_);
    ASSERT_TRUE(r.has_value());
    const auto [q, pen] = simulate(r->q1, r->q4);
    (void)q;
    EXPECT_LT(std::hypot(pen.x - target.x, pen.y - target.y), kReachTol);
  }
}

TEST_F(InverseKinematics, InverseOfForwardIsIdentity)
{
  for (const auto & [q1d, q4d] : jointGrid()) {
    SCOPED_TRACE(testing::Message() << "q1=" << q1d << "° q4=" << q4d << "°");
    const auto p = forwardKinematics({deg(q1d), deg(q4d)}, geometry_);
    ASSERT_TRUE(p.has_value());
    const auto r = inverseKinematics(*p, geometry_);
    ASSERT_TRUE(r.has_value());
    EXPECT_NEAR(wrap(r->q1 - deg(q1d)), 0.0, 1e-9);
    EXPECT_NEAR(wrap(r->q4 - deg(q4d)), 0.0, 1e-9);
  }
}

TEST_F(InverseKinematics, UnreachablePointReturnsNullopt)
{
  EXPECT_TRUE(inverseKinematics({0.07, 0.17}, geometry_).has_value());
  EXPECT_FALSE(inverseKinematics({0.5, 0.5}, geometry_).has_value());  // trop loin
  EXPECT_FALSE(inverseKinematics({0.0, 0.0}, geometry_).has_value());  // sur l'axe moteur
}
