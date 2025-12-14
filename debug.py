#!/usr/bin/env python3
"""
调试和诊断脚本
快速检查项目状态并提供问题诊断
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """检查项目结构"""
    print("🔍 检查项目结构")
    print("=" * 50)

    project_root = Path.cwd()
    required_dirs = ['data', 'models', 'results', 'logs', 'scripts', 'config']
    required_files = ['main.py', 'deploy.py', 'requirements.txt']

    all_good = True

    print("📁 检查目录:")
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ (不存在)")
            all_good = False

    print("\n📄 检查文件:")
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} (不存在)")
            all_good = False

    return all_good

def check_dependencies():
    """检查依赖"""
    print("\n🔍 检查依赖")
    print("=" * 50)

    dependencies = [
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('datasets', 'Datasets'),
        ('pyarrow', 'PyArrow'),
        ('modelscope', 'ModelScope'),
    ]

    all_good = True

    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_good = False

    # 检查PyArrow兼容性
    try:
        import pyarrow as pa
        import pyarrow.lib as palib

        if hasattr(pa, 'PyExtensionType'):
            print("  ✅ PyArrow PyExtensionType (顶级)")
        else:
            print("  ❌ PyArrow PyExtensionType (顶级)")

        if hasattr(palib, 'PyExtensionType'):
            print("  ✅ PyArrow PyExtensionType (lib)")
        else:
            print("  ❌ PyArrow PyExtensionType (lib)")

    except ImportError:
        print("  ❌ PyArrow 导入失败")

    # 检查datasets兼容性
    try:
        import datasets
        print(f"  ✅ Datasets {datasets.__version__}")

        try:
            from datasets import LargeList
            print("  ✅ Datasets LargeList")
        except ImportError:
            print("  ❌ Datasets LargeList (可能导致modelscope导入失败)")

    except ImportError as e:
        print(f"  ❌ Datasets: {e}")

    return all_good

def check_data():
    """检查数据文件"""
    print("\n🔍 检查数据文件")
    print("=" * 50)

    project_root = Path.cwd()
    train_file = project_root / 'data' / 'train.jsonl'
    test_file = project_root / 'data' / 'test.jsonl'

    all_good = True

    for file_path, name in [(train_file, '训练数据'), (test_file, '测试数据')]:
        if file_path.exists():
            try:
                size = file_path.stat().st_size
                print(f"  ✅ {name}: {size} bytes")
            except Exception as e:
                print(f"  ❌ {name}: 无法读取 ({e})")
                all_good = False
        else:
            print(f"  ❌ {name}: 文件不存在")
            all_good = False

    return all_good

def check_models():
    """检查模型文件"""
    print("\n🔍 检查模型文件")
    print("=" * 50)

    project_root = Path.cwd()
    models_dir = project_root / 'models'

    if not models_dir.exists():
        print("  ⚠️  models/ 目录不存在")
        return False

    model_files = list(models_dir.rglob('*'))
    if model_files:
        print(f"  ✅ 找到 {len(model_files)} 个模型相关文件")
        # 显示最近的几个文件
        for file in sorted(model_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"    • {file.relative_to(project_root)}")
        return True
    else:
        print("  ❌ models/ 目录为空")
        return False

def check_results():
    """检查结果文件"""
    print("\n🔍 检查结果文件")
    print("=" * 50)

    project_root = Path.cwd()
    result_file = project_root / 'results' / 'enhanced_result.jsonl'

    if result_file.exists():
        try:
            size = result_file.stat().st_size
            print(f"  ✅ 结果文件: {size} bytes")
            return True
        except Exception as e:
            print(f"  ❌ 结果文件读取失败: {e}")
            return False
    else:
        print("  ⚠️ 结果文件不存在 (训练后会生成)")
        return True  # 这不是错误，只是还没训练

def run_quick_test():
    """运行快速测试"""
    print("\n🔍 运行快速导入测试")
    print("=" * 50)

    tests = [
        ("import torch; print('PyTorch:', torch.__version__)", "PyTorch"),
        ("import transformers; print('Transformers:', transformers.__version__)", "Transformers"),
        ("import datasets; print('Datasets:', datasets.__version__)", "Datasets"),
        ("from modelscope import MsDataset; print('ModelScope: OK')", "ModelScope"),
        ("from swift.llm import TrainArguments; print('Swift: OK')", "Swift"),
    ]

    all_good = True

    for test_code, name in tests:
        try:
            exec(test_code)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:100]}...")
            all_good = False

    return all_good

def provide_solutions():
    """提供解决方案"""
    print("\n🔧 问题诊断和解决方案")
    print("=" * 50)

    print("如果发现问题，请按以下步骤解决:")
    print()
    print("1. 📦 依赖问题:")
    print("   python fix_pyarrow_manual.py")
    print("   python fix_datasets_compatibility.py")
    print()
    print("2. 🔄 环境重置:")
    print("   pip uninstall -y torch transformers datasets pyarrow modelscope ms-swift")
    print("   python install_deps.py")
    print()
    print("3. 🧪 验证修复:")
    print("   python test_setup.py")
    print("   python debug.py")
    print()
    print("4. 🚀 逐步执行:")
    print("   python main.py --step analysis    # 测试数据处理")
    print("   python main.py --step train       # 测试训练")
    print("   python main.py --step inference   # 测试推理")
    print("   python main.py --step evaluate    # 测试评估")

def main():
    """主函数"""
    print("🐛 项目调试和诊断工具")
    print("=" * 60)

    # 运行各项检查
    structure_ok = check_project_structure()
    deps_ok = check_dependencies()
    data_ok = check_data()
    models_ok = check_models()
    results_ok = check_results()
    test_ok = run_quick_test()

    # 总结
    print("\n" + "=" * 60)
    print("📊 检查结果总结:")
    print("=" * 60)

    checks = [
        ("项目结构", structure_ok),
        ("依赖安装", deps_ok),
        ("数据文件", data_ok),
        ("模型文件", models_ok),
        ("结果文件", results_ok),
        ("导入测试", test_ok),
    ]

    all_good = True
    for name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {name}")
        if not status:
            all_good = False

    print("=" * 60)

    if all_good:
        print("🎉 所有检查通过！项目状态良好。")
        print("可以运行: python deploy.py")
    else:
        print("❌ 发现问题，需要修复。")
        provide_solutions()

if __name__ == '__main__':
    main()
