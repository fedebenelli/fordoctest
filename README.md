# fordoctest
Assure Fortran documentation consistence.

## Motivation
As a project increases in size, it is harder to track the quality of the present
code. In the case of functionality unit testing and coverage metrics can be
enough to ensure there are no problems. But keeping track of correct
documentation needs even more meticulous work, external tools can be used to
help this process (like ![pydoctest](https://github.com/jepperaskdk/pydoctest))
in Python. `fordoctest` aims to be an equivalent tool for Fortran documentation.


## What does it do?

### Running

```bash
fordoctest <ford_project_file> [ford_flags]
```

Right now `fordoctest` is in a pre-alpha state, it will check on all the source
files included in a FORD file and send a warning if any of the following cases
occur:

- More than one module per-file
- Undocumented:
    - Isolated procedures
    - Modules
    - Modules procedures
    - Procedures arguments


### What it _aims_ to do
`fordoctest` aims to be a complete tool that can assure that all the code is
correctly documented.  And maybe also include extra checks like file headers,
file naming checks, usage with other tools beside FORD, like Doxygen and Sphinx.
We'll consider `fordoctest` to be in beta-stage once:

- [ ] It becames FORD agnostic (right now it fully depends on the FORD cli
      parser so it's hard to easy add up methods)
- [ ] Includes documentation checks of all the different kinds entities (like
      not included yet, derived types)
- [ ] Include documentation restrictions (like forcing imperative verbs in a 
      procedure documentation)
- [ ] Fully tested with coverage of at least 90%

## Installation
Since this is still an alpha release, we haven't yet released an installable
on PyPI, but the development version can be installed with `pip` with:

```bash
pip install git+ssh://git@github.com/fedebenelli/fordoctest.git
```