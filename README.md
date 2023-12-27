# pysvt

## About

A simple test case runner in Python that uses TOML configurations and decorator syntax.

## Installation

`pip install pysvt`

## Usage

- Function

    Python

    ```python
    from pysvt import test

    @test("<path_to_TOML_file>")
    def function(arg1: int, arg2: int) -> int:
        return arg1 + arg2
    ```

    TOML

    ```python
    name = ["One and Two", "Two and Three"]
    metadata = ["Add to 3", "Add to 5"]
    i = [[1, 2], [2, 3]]
    o = [3, 5]
    ```

    or

    ```python
    [[cases]]
    name = "One and Two"
    i = [1, 2]
    o = 3
    metadata = "Add to 3"

    [[cases]]
    name = "Two and Three"
    i = [2, 3]
    o = 5
    metadata = "Add to 5"
    ```

    - Input key can be either of - i, in, input, inputs
    - Output key can be either of - o, out, output, outputs

- Class (if you want to test instance methods)

    Python

    ```python
    from pysvt import test

    # Specify the name of the method as the second argument
    @test("<path_to_TOML_file>", "function")
    class Solution:
        def function(self, arg1: int, arg2: int) -> int:
            return arg1 + arg2
    ```

    TOML

    ```python
    name = ["One and Two", "Two and Three"]
    metadata = ["Add to 3", "Add to 5"]
    init = []  # Has to be specified, indicates class constructor arguments
    i = [[1, 2], [2, 3]]
    o = [3, 5]
    ```

    or

    ```python
    [[cases]]
    name = "One and Two"
    i = [1, 2]
    o = 3
    metadata = "Add to 3"
    init = []  # Has to be specified, indicates class constructor arguments

    [[cases]]
    name = "Two and Three"
    i = [2, 3]
    o = 5
    metadata = "Add to 5"
    init = []
    ```

    - Input key can be either of - i, in, input, inputs
    - Output key can be either of - o, out, output, outputs
