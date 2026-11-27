// Harnais de test : simulation MuJoCo HEADLESS du système 5 barres (API C de MuJoCo).
//
// Sert de vérité terrain aux tests du modèle géométrique : on asservit (q1, q4)
// dans la simulation, on attend l'équilibre puis on lit la position du site
// 'pen_tip'. La boucle est fermée par la contrainte d'égalité MuJoCo en A3, ce qui
// fournit une référence indépendante du modèle analytique testé.

#ifndef FIVE_BARS_KINEMATICS__TEST__MUJOCO_FIVE_BARS_HPP_
#define FIVE_BARS_KINEMATICS__TEST__MUJOCO_FIVE_BARS_HPP_

#include <mujoco/mujoco.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <stdexcept>
#include <string>

#include "five_bars_kinematics/kinematics.hpp"

namespace five_bars_test
{

/// Chemin du MJCF : $FIVE_BARS_MJCF sinon celui fixé à la compilation (paquet five_bars_description).
inline std::string modelPath()
{
  if (const char * env = std::getenv("FIVE_BARS_MJCF")) {
    return env;
  }
#ifdef FIVE_BARS_MJCF_PATH
  return FIVE_BARS_MJCF_PATH;
#else
  throw std::runtime_error("Définir FIVE_BARS_MJCF (chemin de five_bars.xml)");
#endif
}

class MujocoFiveBars
{
public:
  explicit MujocoFiveBars(const std::string & path = modelPath())
  {
    char error[1024] = "";
    model_ = mj_loadXML(path.c_str(), nullptr, error, sizeof(error));
    if (!model_) {
      throw std::runtime_error("Chargement MJCF impossible (" + path + ") : " + error);
    }
    data_ = mj_makeData(model_);
    q1_adr_ = model_->jnt_qposadr[id(mjOBJ_JOINT, "joint_q1")];
    q4_adr_ = model_->jnt_qposadr[id(mjOBJ_JOINT, "joint_q4")];
    act_q1_ = id(mjOBJ_ACTUATOR, "act_q1");
    act_q4_ = id(mjOBJ_ACTUATOR, "act_q4");
    pen_ = id(mjOBJ_SITE, "pen_tip");
    a3_l2_ = id(mjOBJ_SITE, "A3_link2");
    a3_l3_ = id(mjOBJ_SITE, "A3_link3");
    reset();
  }

  ~MujocoFiveBars()
  {
    mj_deleteData(data_);
    mj_deleteModel(model_);
  }

  MujocoFiveBars(const MujocoFiveBars &) = delete;
  MujocoFiveBars & operator=(const MujocoFiveBars &) = delete;

  /// Retour à la configuration 'home' (assemblage CAO) puis stabilisation.
  void reset()
  {
    mj_resetDataKeyframe(model_, data_, id(mjOBJ_KEY, "home"));
    mj_forward(model_, data_);
    for (int i = 0; i < 300; ++i) {  // referme exactement la chaîne (keyframe approximative)
      mj_step(model_, data_);
    }
  }

  /// Asservit les servos simulés sur (q1, q4) : rampe de consigne (suivi continu de la
  /// branche d'assemblage), maintien, puis attente de l'équilibre. Renvoie true si convergé.
  bool settle(double q1, double q4, double ramp_time = 0.4, double hold_time = 0.6)
  {
    const double dt = model_->opt.timestep;
    const double c1 = data_->ctrl[act_q1_], c4 = data_->ctrl[act_q4_];
    const int n_ramp = std::max(1, static_cast<int>(ramp_time / dt));
    for (int k = 1; k <= n_ramp; ++k) {
      const double s = static_cast<double>(k) / n_ramp;
      data_->ctrl[act_q1_] = c1 + s * (q1 - c1);
      data_->ctrl[act_q4_] = c4 + s * (q4 - c4);
      mj_step(model_, data_);
    }
    for (int k = 0; k < static_cast<int>(hold_time / dt); ++k) {
      mj_step(model_, data_);
    }
    for (int k = 0; k < 5000; ++k) {
      double vmax = 0.0;
      for (int i = 0; i < model_->nv; ++i) {
        vmax = std::max(vmax, std::abs(data_->qvel[i]));
      }
      if (vmax < 1e-4) {
        return true;
      }
      mj_step(model_, data_);
    }
    return false;
  }

  five_bars_kinematics::JointAngles measuredAngles() const
  {
    return {data_->qpos[q1_adr_], data_->qpos[q4_adr_]};
  }

  five_bars_kinematics::PenPosition penPosition() const
  {
    return {data_->site_xpos[3 * pen_], data_->site_xpos[3 * pen_ + 1]};
  }

  std::array<double, 2> siteXY(const std::string & name) const
  {
    const int s = id(mjOBJ_SITE, name);
    return {data_->site_xpos[3 * s], data_->site_xpos[3 * s + 1]};
  }

  double closureError() const
  {
    const double * a = data_->site_xpos + 3 * a3_l2_;
    const double * b = data_->site_xpos + 3 * a3_l3_;
    return std::sqrt(
      (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2]));
  }

  /// Paramètres géométriques lus dans le modèle MuJoCo (source de vérité des tests).
  five_bars_kinematics::Geometry geometry() const
  {
    auto body_x = [this](const char * n) {return model_->body_pos[3 * id(mjOBJ_BODY, n)];};
    auto site_pos = [this](const char * n, int k) {return model_->site_pos[3 * id(mjOBJ_SITE, n) + k];};
    const double l2 = site_pos("A3_link2", 0);
    return {
      body_x("link4") - body_x("link1"), body_x("link2"), l2, site_pos("A3_link3", 0),
      body_x("link3"), site_pos("pen_tip", 0) - l2, site_pos("pen_tip", 1)};
  }

  const mjModel * model() const {return model_;}

private:
  int id(mjtObj type, const std::string & name) const
  {
    const int i = mj_name2id(model_, type, name.c_str());
    if (i < 0) {
      throw std::runtime_error("Élément MuJoCo introuvable : " + name);
    }
    return i;
  }

  mjModel * model_{nullptr};
  mjData * data_{nullptr};
  int q1_adr_{}, q4_adr_{}, act_q1_{}, act_q4_{}, pen_{}, a3_l2_{}, a3_l3_{};
};

}  // namespace five_bars_test

#endif  // FIVE_BARS_KINEMATICS__TEST__MUJOCO_FIVE_BARS_HPP_
