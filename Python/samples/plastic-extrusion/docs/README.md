# A Note on the Equations

Our [mathematical model](./model.md) of the extrusion process has over two dozen equations.

While GitHub can render mathematical equations in Markdown cells in [Jupyter](https://gist.github.com/cyhsutw/d5983d166fb70ff651f027b2aa56ee4e) [notebooks](https://github.com/jupyter/nbformat/blob/master/docs/markup.rst), GitHub has been [curiously](https://github.com/github/markup/issues/274) [reluctant](https://github.com/github/markup/issues/897) to include support for equations in Markdown and [reStructuredText](https://github.com/github/markup/issues/83) documents.

A [few](https://github.com/leegao/readme2tex) [workarounds](https://gist.github.com/a-rodin/fef3f543412d6e1ec5b6cf55bf197d7b) exist, but these methods lack the convenience of native support, and there is no guarantee that they will work long term.

Fortunately, Visual Studio Code has [native support for rendering equations in Markdown documents with KaTeX](https://code.visualstudio.com/updates/v1_58#_math-formula-rendering-in-the-markdown-preview), so we recommend cloning or downloading this repository to your local machine and rendering the equations with VS Code.
