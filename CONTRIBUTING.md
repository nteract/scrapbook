# So You Want to Contribute to Scrapbook!

We welcome all contributions to Scrapbook both large and small. We encourage you
to join our community.

## Our Community Values

We are an open and friendly community. Everybody is welcome.

We encourage friendly discussions and respect for all. There are no
exceptions.

All contributions are equally important. Documentation, answering questions,
and fixing bugs are equally as valuable as adding new features.

Please read our entire code of conduct
[here](https://github.com/nteract/nteract/blob/master/CODE_OF_CONDUCT.md).
Also, check out the for the
[Python](https://github.com/nteract/nteract/blob/master/CODE_OF_CONDUCT.md)
code of conduct.

## Setting up Your Development Environment

Following these instructions should give you an efficient path to opening your
 first pull-request.

### Cloning the Scrapbook Repository

Fork the repository to your local Github
account. Clone this repository to your local development machine. 

```bash
git clone https://github.com/<your_account>/scrapbook 
cd scrapbook
```

### Install an Editable Version
We prefer to use [conda](https://conda.io/docs/user-guide/tasks/manage-environments.html) to manage the development environment.
```bash
conda create -n dev
. activate env
```
or use native venv capabilities if you prefer.
```bash
python3 -m venv dev
```

Install Scrapbook using:

```bash
pip install -e .[dev]
```

_Note: When you are finished you can use `source deactivate` to go back to your base environment._

### Running Tests Locally

We need to install the development package before we can run the tests. If anything is confusing below, always resort to the relevant documentation.

For the most basic test runs against python 3.6 use this tox subset (callable after `pip install tox`):
```bash
tox -e py36
```
This will just execute the unittests against python 3.6 in a new virtual env. The first run will take longer to setup the virtualenv, but will be fast after that point.

For a full test suite of all envs and linting checks simply run tox without any arguments
```bash
tox
```
This will require python2.7, python3.5, python3.6, and python3.7 to be installed. **Note** that python 3.7 has problems with the alpha build which is the available package version on many linux distros. Local build failures with 3.7 can happen as a result (you'll see a seg fault or exist code -11).

Alternavitely pytest can be used if you have an environment already setup which works or has custom packages not present in the tox build.
```bash
pytest --pyargs scrapbook
```

The `pyargs` option allows `pytest` to interpret arguments as python package
names. An advantage is that `pytest` will run in any directory, and this
approach follows the `pytest` [best
practices](https://docs.pytest.org/en/latest/goodpractices.html#tests-as-part-
of-application-code).

Now there should be a working and editable installation of Scrapbook to start
making your own contributions.

## So You're Ready to Pull Request

The general workflow for this will be:

1. Run local tests
2. Pushed changes to your forked repository
3. Open pull request to main repository

### Push Changes to Forked Repo

Your commits should be pushed to the forked repository. To verify this type 

```bash
git remote -v
``` 

and ensure the remotes point to your GitHub. Don't work on the master branch!

1. Commit changes to local repository:

    ```bash
    git checkout -b my-feature
    git add <updated_files>
    git commit
    ```
2. Push changes to your remote repository:

    ```bash
    git push -u origin my-feature
    ```

### Create Pull Request

Follow [these](https://help.github.com/articles/creating-a-pull-request-
from-a-fork/) instructions to create a pull request from a forked repository.
If you are submitting a bug-fix for a specific issue make sure to reference
the issue in the pull request.

There are good references to the [Git documentation](https://git-scm.com/doc)
and [Git workflows](https://docs.scipy.org/doc/numpy/dev/gitwash/development_w
orkflow.html) for more information if any of this is unfamiliar.

_Note: You might want to set a reference to the main repository to fetch/merge from there instead of your forked repository. You can do that using:_

```bash
git remote add upstream https://github.com/nteract/scrapbook
```

It's possible you will have conflicts between your repository and master. Here,
`master` is meant to be synchronized with the `upstream` repository.  GitHub has
some good [documentation](https://help.github.com/articles/resolving-a-merge-conflict-using-the-command-line/)
on merging pull requests from the command line.

## Contributing to Scrapbook Documentation

1. Set up a virtual environment and activate it.

```bash
python3 -m venv mydocs
source mydocs/bin/activate
```

2. From the repo's root directory, install dependencies needed for documentation
   and the development version of Scrapbook:

```bash
pip install -r docs/requirements-doc.txt
pip install -e .
```

3. Change to the `docs` directory and clean out any stale documentation builds:

```bash
cd docs
make clean
```

4. Build the documentation

```bash
make html
```

If the build succeeds, it will display a message letting you know where to find
the documentation:

```bash
The HTML pages are in _build/html.
```

5. Serve the documentation locally

```bash
python -m http.server
```

This will return a message letting you know where to direct your browser:

```bash
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```



Happy hacking on Scrapbook!
