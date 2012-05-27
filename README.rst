*************
cuisine_sweet
*************

Sugar-coated declarative deployment recipes built on top of `Fabric <http://fabfile.org>`_ 
and `Cuisine <https://github.com/sebastien/cuisine>`_.

With Fabric's low-level remote ssh orchestration and Cuisine's generic recipes; the goal
is to build a collection of wrappers capturing various, usually opinionated, system deployment 
styles.

At the heart of ``cuisine_sweet`` is the collection of ``ensure`` modules. These modules encapsulate
what is being checked/deployed (declarative), without specifying the how and the where parts
(imperative). An ensure is both an assertion check + action-if-needed in the form: 
``ensure.object.state(params)``.

- `Source Code <http://github.com/dexterbt1/cuisine_sweet>`_
- `Documentation <http://cuisine_sweet.readthedocs.org/>`_
- Feedback / Patches - `Create an issue <http://github.com/dexterbt1/cuisine_sweet/issues>`_

