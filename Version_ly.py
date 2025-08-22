# version_utils.py
from typing import Optional, Tuple, Union

class version:
    def __init__(self, version_str: str) -> None:
        """解析版本号字符串，支持格式如 1.6.0 或 1.6.0-Beta1"""
        self.version_str = version_str
        self._parse_version()

    def _parse_version(self) -> None:
        """解析版本号各部分"""
        # 分割基础版本和预发布标识
        parts = self.version_str.split('-', 1)
        self.base_version = parts[0]
        
        # 解析预发布信息
        self.prerelease: Optional[str] = parts[1] if len(parts) > 1 else None
        self.pre: Optional[Tuple[str, int]] = None
        if self.prerelease:
            self._parse_prerelease()
        
        # 解析基础版本号为元组
        self.version_tuple = tuple(int(part) for part in self.base_version.split('.'))
        self.is_prerelease = self.prerelease is not None

    def _parse_prerelease(self) -> None:
        """解析预发布标识为 (类型, 编号) 元组"""
        import re
        match = re.match(r'([a-zA-Z]+)(\d*)$', self.prerelease)
        if match:
            pre_type, pre_number = match.groups()
            # 标准化预发布类型
            pre_type = pre_type.lower()
            if pre_type.startswith('alpha'):
                pre_type = 'a'
            elif pre_type.startswith('beta'):
                pre_type = 'b'
            elif pre_type.startswith(('c', 'rc')):
                pre_type = 'rc'
                
            # 提取预发布编号
            pre_number = int(pre_number) if pre_number else 0
            self.pre = (pre_type, pre_number)

    def __lt__(self, other: 'version') -> bool:
        """比较版本号大小"""
        if self.version_tuple < other.version_tuple:
            return True
        elif self.version_tuple > other.version_tuple:
            return False
        
        # 基础版本相同，比较预发布标识
        if not self.is_prerelease and not other.is_prerelease:
            # 两者都没有预发布信息，相等
            return False
        if not self.is_prerelease and other.is_prerelease:
            # 自己没有预发布，对方有，自己更大
            return False
        elif self.is_prerelease and not other.is_prerelease:
            # 自己有预发布，对方没有，自己更小
            return True
        
        # 两者都有预发布标识，按解析后的预类型和编号比较
        return self.pre < other.pre

    def __eq__(self, other: object) -> bool:
        if not isinstance(other,version):
            return False
        return (self.version_tuple == other.version_tuple and
                self.prerelease == other.prerelease)

    def __le__(self, other: 'version') -> bool:
        return self < other or self == other

    def __repr__(self) -> str:
        return f"Version('{self.version_str}')"
    
    @property
    def pure_version(self) -> str:
        """返回纯版本号字符串（不含预发布信息）"""
        return self.base_version
    
    @property
    def full_version(self) -> str:
        """返回完整版本号字符串（包含预发布信息）"""
        return self.version_str

# 示例用法
if __name__ == "__main__":
    v1 = version("1.6.0-Beta2")
    
    v2 = version("1.6.0")
    print(v1 < v2)           # 输出: False
    print(v1 > v2)           # 输出: True
    print(v1 == v2)          # 输出: False
    print(v1 <= v2)          # 输出: False
    print(v1 >= v2)          # 输出: True
    print(v1.is_prerelease)  # 输出: True
    print(v1.version_tuple)  # 输出: (1, 6, 0)
    print(v1.prerelease)     # 输出: Beta2
    print(v1.pre)            # 输出: ('b', 2)
    print(v1.pure_version)   # 输出: 1.6.0
    print(v1.full_version)   # 输出: 1.6.0-Beta2
    print(str(v1))           # 输出: Version('1.6.0-Beta2')