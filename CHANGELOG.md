# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2024-06-29

### Changed

- Input argument names along with values instead of the previous list of inputs

### Removed

- Live mode (`is_live` parameter)

## [0.4.3] - 2024-06-20

### Fixed

- Unnecessary print in the source code.

## [0.4.1] - 2024-06-07

### Changed

- Font weight of panel titles (Input, Expected output, etc) to bold

### Fixed

- Inconsistent inputs being displayed due to mutation of the inputs occuring in the executed function.

## [0.4.0] - 2024-06-07

### Added

- `pretty_print_errors` parameter to pretty print errors with colors and more information.
- `redirect_stdout` parameter to redirect all stdout (print statements, etc) to the pretty printed panels.
- New examples for the above parameters.

### Removed

- The loading animation when executing the decorator.

## [0.3.0] - 2024-01-01

### Added

- `preprocess` parameter to process inputs before being called by the passed function.
- `postprocess` parameter to process outputs before validation.
- `is_live` parameter to set the printing mode and made it default to False (results are printed sequentially and not updated in real time).

### Changed

- Examples to better reflect the updated code.
