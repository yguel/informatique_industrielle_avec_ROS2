###################################################
Description mécanique de la plateforme pantographe
###################################################

.. géométrie du pantographe
.. cinématique du pantographe
.. dynamique du pantographe


.. figure:: resources/img/schema_cinematique.svg
   :align: center


Modèle géométrique 
==================

Nous avons :

.. math:: 
   \overrightarrow{A_1A_2} + \overrightarrow{A_2A_3} + \overrightarrow{A_3A_4} = \overrightarrow{A_1A_5} + \overrightarrow{A_5A_4}

En projetant sur l'axe :math:`\overrightarrow{x}` et :math:`\overrightarrow{y}`, nous obtenons :

.. math::

   \begin{aligned}
      \begin{cases}
         l_1 c_1 + l_2 c_2 + l_3 c_3 = l_0 + l_4 c_4 \\
         l_1 s_1 + l_2 s_2 + l_3 s_3 = l_4 s_4
      \end{cases}
      \quad \Longleftrightarrow \quad
      \begin{cases}
         l_1 c_1 + l_2 c_2 - l_0 - l_4 c_4 = -l_3 c_3  \\
         l_1 s_1 + l_2 s_2 - l_4 s_4 = - l_3 s_3
      \end{cases}
   \end{aligned}

Nous avons donc deux équation pour deux inconnues : :math:`\theta_2` et :math:`\theta_3`. :math:`\theta_1` et :math:`\theta_4` sont les variables d'entrées du mécanisme. 

En additionnant les deux équations au carré, nous obtenons une équation sans :math:`\theta_3` :

.. math::

   \begin{aligned}
   (l_1 c_1 + l_2 c_2 - l_0 - l_4 c_4)^2 + (l_1 s_1 + l_2 s_2 - l_4 s_4)^2 &= l_3^2 \\
   \Longleftrightarrow\quad
   l_1^2 + l_2^2 + l_4^2 + l_0^2 - l_3^2
   - 2l_1l_0c_1 - 2l_1l_4c_1c_4 + 2l_0l_4c_4 - 2l_1l_4s_1s_4 \\
   \qquad + 2c_2l_2(l_1c_1 - l_0 - l_4c_4) + 2s_2l_2(l_1s_1 - l_4s_4) &= 0
   \end{aligned}

Nous fixons :

.. math::

   \begin{aligned}
   M &= l_1^2 + l_2^2 + l_4^2 + l_0^2 - l_3^2
        - 2l_1l_0c_1 - 2l_1l_4c_1c_4 + 2l_0l_4c_4 - 2l_1l_4s_1s_4 \\
   L &= 2l_2(l_1c_1 - l_0 - l_4c_4) \\
   K &= 2l_2(l_1s_1 - l_4s_4)
   \end{aligned}


Nous obtenons donc l'équation suivante, qui ne dépend que de :math:`\theta_2` :

 .. math::

   M + c_2L + s_2K = 0\\

Nous pouvons remplacer c2 et s2 par leur expression en fonction de tan(:math:`\frac{\theta_2}{2}`) :

.. math::

   t = tan(\frac{\theta_2}{2})\\
   c_2 = \frac{1 - t^2}{1+t^2}\\
   s_2 = \frac{2t}{1+t^2}\\

Nous obtenons donc :

.. math::

   \begin{aligned}
      L(1-t^2) + 2Kt = - M (1 + t^2)\\
   \quad \Longleftrightarrow \quad
      t^2(M-L)+2Kt + L + M;
   \end{aligned}

Nous avons une équation de polynomiale de degré 2, nous pouvons donc calculer t :

.. math::

   t = \frac{-2K \pm \sqrt{(2K)^2-4(M-L)(M+L)}}{2(M - L)}\\

Ainsi :

.. math::

   \theta_2 = 2arctan(t)

Avec :math:`\theta_2` et connaissant :math:`\theta_1`, nous pouvons caluler la position X3 et Y3 du point :math:`A_3` :

.. math::

   X3 = l_1c_1 + l_2c_2\\
   Y3 = l_1s_2 + l_2s_2




