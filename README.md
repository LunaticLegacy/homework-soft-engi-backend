## 后端工程

Based on `Python 3.13.5`

### 需求：

需要导入的库：
- `redis`：用于管理缓存
- `asyncpg`：用于管理postgresql数据库，异步
- `fastapi`：用于构建后端服务器及路由

使用该命令：
```
pip install -r ./requirements.txt
```
以一键导入所需库。（注意：`开发之前，必须创建虚拟环境`。）

### 开发规范：

请`fork`一份本仓库，并创建一个新的分支，随后签出到创建的分支。
- 你的所有改动都必须放在这个分支上，并上传到你自己fork后的仓库。
- 确定代码完工后，请对主仓库发起`pull request`。
- 本代码采用模块化开发。
    - 请在`utils`文件夹内为你的模块创建一个文件夹，并在文件夹内写入模块。

### 代码规范：

1. 当一个变量被初次创建时，必须写类型注解。
```python
def blablabla() -> None:
    a: int = 3  # 第一次定义时必须写类型注解
    a = 4       # 后赋值可以省略
```

2. 函数的输入类型及输出类型必须写类型注解，且函数必须写说明。（我习惯用Google风的参数描述）
```python
def func1(a: int, b: float) -> float:
    """
    乘法操作。
    Args:
        a (int): 第一个数字。
        b (float): 第二个数字。
    Returns:
        (float): 乘积。
    """
    return a * b
```

3. 关于库`typing`，如果需要标注元组或列表，或者其他数据类型，可以从内置的`typing`库里引入标注。
```python
from typing import List, Tuple, Dict, Any, Optional
# 这个库还有一堆东西，问deepseek或豆包吧
```
例：
```python
def get_user_ids() -> List[int]:
    return [1, 2, 3]
```

4. 返回多个值时使用`Dict`
- **禁止返回裸列表或元组。**
- 如果需要一次传出多个值，请使用`Dict`——严禁使用`List`或`Tuple`。
```python
# 错误示例
def func3() -> List:
    """
    错误示例函数。如果直接返回一个List，那么接下来这个List被如何解析就全看调用者如何进行。
    我曾经搞过一个传入List的结构，当时的元素将近30多个。
    只要我增加/删除了其中一个元素，那么后来的代码工作量会极为巨大——数组下标必须被全部更改。
    """
    return [404, "Not found"]

# 正确示例
from typing import Any

def correct_func3() -> Dict[str, Any]:
    """
    如果未来会有其他位置需要使用该函数，该函数的更改导致的代码更改量就不会再那么大了。
    因为所有的值都是有一个键所对应的。
    """
    return {
        "code": 404,
        "message": "Not found"
    }

```

5. 命名规范：
- 所有的类名必须为开头大写，例：`DatabaseManager`。
- 函数名全小写，单词之间用`_`分割。例：`function_in_class`。
- 如果需要定义类内私有函数，在函数名前加一个`_`。例：`_a_private_function`。
