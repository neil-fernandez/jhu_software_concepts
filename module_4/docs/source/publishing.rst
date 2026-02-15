Build and Publish Docs (GitHub)
===============================

Local Build
-----------

From repository root:

.. code-block:: bash

   pip install -r module_4/requirements.txt
   sphinx-build -b html module_4/docs/source module_4/docs/_build/html

Published Output
----------------

Built HTML is generated at:
``module_4/docs/_build/html``

GitHub Pages Workflow
---------------------

This repo includes a Pages workflow at:
``.github/workflows/docs.yaml``

It:

1. Installs Python and dependencies.
2. Builds Sphinx HTML docs.
3. Uploads the artifact.
4. Deploys to GitHub Pages.

Repository Settings Required
----------------------------

In GitHub repository settings:

1. Open ``Settings -> Pages``.
2. Set source to ``GitHub Actions``.
3. Ensure workflow permissions allow Pages deployments.

Triggering Publish
------------------

Docs deployment runs automatically on pushes to ``main`` affecting:

1. ``module_4/docs/**``
2. ``module_4/src/**``
3. ``.github/workflows/docs.yaml``

You can also trigger it manually from the Actions tab using
``workflow_dispatch``.

