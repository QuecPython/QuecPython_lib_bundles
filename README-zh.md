# QuecPython_lib_bundles 代码提交说明

[[English](./README.md)]

## 目录结构示例

```
.
|-- README.md               --- QuecPython_lib_bundles 代码提交说明
|-- images                  --- 存储 md 文件引用的图片
|   |-- ads1115                 --- 以库的名称建立文件夹，分类存储图片
|   `-- bmp280                  --- 同上
`-- libraries               --- 存储库代码和文档
    |-- ads1115                 --- 以库的名称建立文件夹，分类存储库代码和文档
    |   |-- README.md               --- 应用指导文档
    |   |-- ads1115.py              --- 库代码
    |   `-- ads1115_demo.py         --- demo示例
    `-- bmp280              --- 同上
        |-- README.md
        |-- bmp280.py
        `-- bmp280_demo.py
```

> 代码贡献者请严格遵守该目录结构的约束。

## 代码提交

- 请先fork本仓库至个人账号，贡献的代码提交至仓库的dev分支，而后向源仓库的dev分支提PR，管理员审核通过后，合入到源仓库dev分支，并定期同步到master分支。

- 使用`git config commit.template ./commit.template`命令配置日志提交模板，使用`git commit`命令（不携带任何参数）进行提交，以便更好地遵守模板的规范。

- 代码提交者的git配置的邮箱请保证真实有效，以便管理员与其沟通。
