# QuecPython_lib_bundles Code Submission Guidelines

[[中文](./README-zh.md)]

## Directory Structure Example

```
.
|-- README.md               --- QuecPython_lib_bundles Code Submission Guidelines
|-- images                  --- Stores images referenced in the markdown files
|   |-- ads1115                 --- Create folders based on library names to categorize images
|   `-- bmp280                  --- Same as above
`-- libraries               --- Stores library code and documentation
    |-- ads1115                 --- Create folders based on library names to categorize library code and documentation
    |   |-- README.md               --- Application guide document
    |   |-- ads1115.py              --- Library code
    |   `-- ads1115_demo.py         --- Demo
    `-- bmp280              --- Same as above
        |-- README.md
        |-- bmp280.py
        `-- bmp280_demo.py
```

> Code contributors are required to strictly adhere to this directory structure.

## Code Submission

- Please fork this repository to your personal account. Contribute your code to the dev branch of your own fork. Then, create a pull request (PR) from your dev branch to the dev branch of the source repository. After the PR is reviewed and approved by the administrators, it will be merged into the source repository's dev branch and periodically synchronized to the master branch.

- Use the `git config commit.template ./commit.template` command to configure the commit template. When making commits with the `git commit` command (without any parameters), follow the template for better adherence to commit message guidelines.

- Make sure your git configuration email is accurate and valid for effective communication with the administrators.
