"""
从 veighna_studio 复制缺失的 DLL 到 resources 目录

用法:
    python scripts/copy_dlls.py
"""

import shutil
from pathlib import Path
from typing import List

# 源目录和目标目录
VEIGHNA_STUDIO = Path(r"C:\veighna_studio")
RESOURCES_DIR = Path(__file__).parent.parent / "resources" / "dlls"
PROJECT_ROOT = Path(__file__).parent.parent

# 需要查找的 DLL 文件
REQUIRED_DLLS = [
    # Visual C++ 运行时
    "MSVCP120.dll",  # Visual C++ 2013
    "MSVCR120.dll",  # Visual C++ 2013
    "mfc100.dll",    # MFC 库
    "python37.dll",  # Python 3.7 DLL（某些旧版扩展需要）
    "vcruntime140.dll",  # Visual C++ 2015-2022
    "vcruntime140_1.dll",  # Visual C++ 2015-2022
    # 其他可能的依赖
    "msvcp140.dll",
    "msvcp140_1.dll",
    "msvcp140_2.dll",
    "msvcp140_codecvt_ids.dll",  # PySide6 可能需要
    "vcomp140.dll",
    "mfc140u.dll",  # MFC 库（某些工具可能需要）
]


def find_dll_in_veighna(dll_name: str) -> Path | None:
    """在 veighna_studio 中查找 DLL 文件"""
    search_paths = [
        VEIGHNA_STUDIO / "DLLs",
        VEIGHNA_STUDIO,
        VEIGHNA_STUDIO / "Lib" / "site-packages",
    ]
    
    # 递归搜索
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # 在当前目录查找
        dll_path = search_path / dll_name
        if dll_path.exists():
            return dll_path
        
        # 递归搜索
        for dll_file in search_path.rglob(dll_name):
            if dll_file.is_file():
                return dll_file
    
    return None


def find_dll_in_system(dll_name: str) -> Path | None:
    """在系统目录中查找 DLL 文件"""
    system_paths = [
        Path(r"C:\Windows\System32"),
        Path(r"C:\Windows\SysWOW64"),
    ]
    
    for sys_path in system_paths:
        dll_path = sys_path / dll_name
        if dll_path.exists():
            return dll_path
    
    return None


def copy_dlls() -> None:
    """复制缺失的 DLL 文件"""
    print("=" * 60)
    print("从 veighna_studio 复制缺失的 DLL 文件")
    print("=" * 60)
    
    # 创建目标目录
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    
    copied = []
    not_found = []
    
    for dll_name in REQUIRED_DLLS:
        # 先检查目标文件是否已存在
        target_path = RESOURCES_DIR / dll_name
        if target_path.exists():
            print(f"  [跳过] {dll_name} (已存在)")
            continue
        
        # 在 veighna_studio 中查找
        source_path = find_dll_in_veighna(dll_name)
        
        # 如果没找到，尝试在系统目录查找
        if not source_path:
            source_path = find_dll_in_system(dll_name)
        
        if source_path:
            try:
                shutil.copy2(source_path, target_path)
                print(f"  [复制] {dll_name} <- {source_path}")
                copied.append(dll_name)
            except Exception as e:
                print(f"  [错误] {dll_name}: {e}")
                not_found.append(dll_name)
        else:
            print(f"  [未找到] {dll_name}")
            not_found.append(dll_name)
    
    print("=" * 60)
    print(f"完成！复制了 {len(copied)} 个文件")
    if not_found:
        print(f"未找到 {len(not_found)} 个文件: {', '.join(not_found)}")
        print("\n提示: 这些 DLL 可能需要安装 Visual C++ Redistributable")
        print("      MSVCP120.dll/MSVCR120.dll 需要 Visual C++ 2013 Redistributable")
        print("      vcruntime140.dll 需要 Visual C++ 2015-2022 Redistributable")
    print("=" * 60)


if __name__ == "__main__":
    if not VEIGHNA_STUDIO.exists():
        print(f"错误: veighna_studio 目录不存在: {VEIGHNA_STUDIO}")
        print("请检查路径是否正确")
        exit(1)
    
    copy_dlls()
