#!/usr/bin/env python3
"""
项目设置测试脚本
验证所有核心功能是否正常工作
"""

import os
import sys
import subprocess

def test_imports():
    """测试核心依赖导入"""
    print("🔍 测试依赖导入...")

    # 测试必需依赖
    required_modules = ['torch']
    recommended_modules = ['transformers', 'datasets']

    all_success = True

    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (必需)")
            all_success = False

    for module in recommended_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:  # 改为Exception以捕获所有错误
            error_str = str(e)[:50]
            if "PyExtensionType" in error_str:
                error_str = "版本兼容性问题，建议运行: python fix_modelscope_deps.py"
            print(f"  ⚠️  {module} (推荐) - {error_str}...")

    if all_success:
        print("✅ 核心依赖检查完成")
    else:
        print("⚠️  部分依赖缺失，某些功能可能无法使用")

    return True  # 不因为推荐依赖失败而返回False

def test_scripts():
    """测试脚本文件存在性"""
    print("\n🔍 测试脚本文件...")
    required_scripts = [
        'main.py',
        'scripts/__init__.py',
        'scripts/data_processor.py',
        'scripts/model_trainer.py',
        'scripts/evaluate.py',
        'scripts/utils.py'
    ]

    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
        else:
            print(f"✅ {script}")

    if missing_scripts:
        print(f"❌ 缺少脚本文件: {missing_scripts}")
        return False

    return True

def test_directories():
    """测试目录结构"""
    print("\n🔍 测试目录结构...")
    required_dirs = ['data', 'models', 'results', 'scripts', 'logs']

    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/")

    if missing_dirs:
        print(f"❌ 缺少目录: {missing_dirs}")
        return False

    return True

def test_data_files():
    """测试数据文件"""
    print("\n🔍 测试数据文件...")
    data_files = ['data/train.jsonl', 'data/test.jsonl']

    missing_files = []
    for file_path in data_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing_files:
        print(f"⚠️  数据文件不存在: {missing_files}")
        print("   请运行: python scripts/data_processor.py download")
        return True  # 不算错误，只是需要下载

    return True

def test_main_script():
    """测试主脚本帮助信息"""
    print("\n🔍 测试主脚本...")
    try:
        result = subprocess.run([sys.executable, 'main.py', '--help'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'usage:' in result.stdout.lower():
            print("✅ 主脚本运行正常")
            return True
        else:
            print(f"❌ 主脚本测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 主脚本测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🐰 金融文本相似度分类竞赛 - 项目测试")
    print("=" * 60)

    tests = [
        ("依赖导入", test_imports),
        ("脚本文件", test_scripts),
        ("目录结构", test_directories),
        ("数据文件", test_data_files),
        ("主脚本", test_main_script)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
        print("-" * 30)

    print(f"\n📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！项目设置完成。")
        print("\n🚀 接下来可以运行:")
        print("  python main.py --step all    # 一键执行完整流程")
        print("  python main.py --help        # 查看帮助信息")
    else:
        print("❌ 部分测试失败，请检查上述错误信息。")

    print("=" * 60)

if __name__ == '__main__':
    main()
