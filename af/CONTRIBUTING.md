# Prognos Cloud Repository

## Contributing guidelines

To contribute to this repository, please use the following guidelines.

### Working Branch Naming

Are you working on a given feature of the project ? If so, below are some recommendations.
* Add a feature by creating a new branch with a prefix "feature/add-" (e.g. "feature/add-emr-preprocessing-steps")
* Change a feature by creating a new branch with a prefix "feature/change-" (e.g. "feature/change-emr-preprocessing-steps")
* Remove a feature by creating a new branch with a prefix "feature/remove-" (e.g. "feature/remove-emr-preprocessing-steps")

Did you find a bug ? If so, below are some recommendations.
* Add a bug correction by creating a new branch with a prefix "bug/" (e.g. "bug/emr-preprocessing-steps") 

Are you cleaning and formatting the code ? If so, below are some recommendations.
* Except for specific reasons explained and accepted by developers, changes that are cosmetic in nature and do not add anything substantial to the stability, functionality, or testability will not be accepted. Any changement in the code should already follow standard rules of code formatting (PEP8) and tools are provided to keep with this goal (pre-commit).

### Testing Policy

Any part of the code must be executed and tested with unit tests (see pytest-coverage).
Changes in the code must lead to add, edit or remove unit tests depending on whether features are added, changed or removed.

### Branch Lifecycle

Please keep your branch for 3 to 6 months. Every branch with higher life time should be removed, except if the developers have reasons for keeping it.

### Project Architecture


