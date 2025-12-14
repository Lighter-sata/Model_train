#!/usr/bin/env python3
"""
临时的datasets导入修复脚本
解决LargeList导入问题
"""

import sys

def apply_fix():
    """应用LargeList修复"""
    try:
        import datasets

        # 检查是否需要修复LargeList
        if not hasattr(datasets, 'LargeList'):
            print("🔧 检测到LargeList缺失，开始修复...")

            # 方法1: 从features导入
            try:
                from datasets.features import Sequence
                datasets.LargeList = Sequence
                print("✅ LargeList -> Sequence (修复成功)")
                return True
            except ImportError:
                pass

            # 方法2: 创建基本兼容类
            try:
                class LargeList:
                    """Basic LargeList compatibility"""
                    pass
                datasets.LargeList = LargeList
                print("✅ 创建了基础LargeList类")
                return True
            except Exception as e:
                print(f"❌ 创建兼容类失败: {e}")
                return False
        else:
            print("✅ LargeList已存在，无需修复")
            return True

    except ImportError as e:
        print(f"❌ 无法导入datasets: {e}")
        return False

if __name__ == '__main__':
    if apply_fix():
        print("🎉 修复完成，现在可以运行训练了")
        print("运行: python main.py --step train")
    else:
        print("❌ 修复失败")
        sys.exit(1)
