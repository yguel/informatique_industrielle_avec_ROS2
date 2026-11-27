from setuptools import find_packages, setup

package_name = "five_bars_mujoco"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    extras_require={"test": ["pytest"]},
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="todo@example.com",
    description="Simulation MuJoCo du système 5 barres + nœuds ROS 2",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "direct_gui = five_bars_mujoco.direct_gui:main",
            "sim_node = five_bars_mujoco.sim_node:main",
            "slider_gui = five_bars_mujoco.slider_gui_node:main",
            "state_updater = five_bars_mujoco.state_updater_node:main",
        ],
    },
)
