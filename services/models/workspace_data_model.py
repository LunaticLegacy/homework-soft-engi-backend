from dataclasses import dataclass

# 先别用这个东西，我现在需要得到这个东西对应的数据类型。

@dataclass
class WorkspaceData:
    id: str
    name: str
    description: str
    owner_user_id: str
    created_at: str
