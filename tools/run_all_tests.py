"""
快速运行所有平台测试的脚本

使用方法:
    python tools/run_all_tests.py
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def run_tests(markers=None, verbose=True):
    """
    运行测试

    Args:
        markers: pytest标记，如 'bilibili', 'douyin', 'xiaohongshu'
        verbose: 是否显示详细输出
    """
    cmd = [sys.executable, '-m', 'pytest', str(PROJECT_ROOT / 'tests')]

    if verbose:
        cmd.append('-v')

    if markers:
        cmd.extend(['-m', markers])

    # 添加其他选项
    cmd.extend([
        '--tb=short',  # 简短的traceback
        '--color=yes',  # 彩色输出
    ])

    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """主函数"""
    print("测试运行器")
    print("=" * 60)

    print("\n请选择要运行的测试:")
    print("  1. 运行所有测试")
    print("  2. 仅运行B站测试")
    print("  3. 仅运行抖音测试")
    print("  4. 仅运行小红书测试")
    print("  5. 运行快速测试（跳过slow标记）")
    print("  0. 退出")

    choice = input("\n请选择 [0-5]: ").strip()

    if choice == '1':
        returncode = run_tests()
    elif choice == '2':
        returncode = run_tests(markers='bilibili')
    elif choice == '3':
        returncode = run_tests(markers='douyin')
    elif choice == '4':
        returncode = run_tests(markers='xiaohongshu')
    elif choice == '5':
        returncode = run_tests(markers='not slow')
    elif choice == '0':
        print("退出")
        return 0
    else:
        print("无效选择")
        return 1

    print("\n" + "=" * 60)
    if returncode == 0:
        print("测试通过!")
    else:
        print(f"测试失败，返回码: {returncode}")

    return returncode


if __name__ == '__main__':
    sys.exit(main())
