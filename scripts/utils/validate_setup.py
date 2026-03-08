"""Validation script to check TraceGuard AI setup and dependencies"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10 or higher"""
    print("✓ Checking Python version...", end=" ")
    if sys.version_info >= (3, 10):
        print(f"✓ Python {sys.version.split()[0]} (OK)")
        return True
    else:
        print(f"✗ Python {sys.version.split()[0]} (FAILED - requires 3.10+)")
        return False


def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed"""
    import_name = import_name or package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n✓ Checking dependencies...")

    required_packages = {
        "pydantic": "pydantic",
        "yaml": "yaml",
        "evtx": "Evtx",
        "scapy": "scapy",
        "sentence_transformers": "sentence_transformers",
        "faiss": "faiss",
        "numpy": "numpy",
        "llama_index": "llama_index",
        "tqdm": "tqdm",
    }

    missing_packages = []

    for package, import_name in required_packages.items():
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ✗ {package} (NOT INSTALLED)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n✗ Missing dependencies: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False

    print("✓ All dependencies installed")
    return True


def check_ollama_service():
    """Check if Ollama service is running and accessible"""
    print("\n✓ Checking Ollama service...", end=" ")

    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama service is running")
            models = response.json().get("models", [])
            if models:
                model_names = [m.get("name", "unknown") for m in models]
                print(f"  Available models: {', '.join(model_names)}")
                if any("qwen2.5" in m.lower() or "qwen" in m.lower() for m in model_names):
                    print("  ✓ Qwen2.5 model found")
                    return True
                else:
                    print("  ✗ Qwen2.5 model not found")
                    print("  Pull it with: ollama pull qwen2.5:3b")
                    return False
            else:
                print("  ⚠ No models found")
                print("  Pull Qwen2.5 with: ollama pull qwen2.5:3b")
                return False
        else:
            print(f"✗ Ollama service returned status {response.status_code}")
            return False
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"✗ Cannot connect to Ollama (http://localhost:11434)")
        print("  Make sure Ollama is installed and running:")
        print("  1. Download from https://ollama.ai")
        print("  2. Start Ollama: ollama serve")
        print("  3. In another terminal: ollama pull qwen2.5:3b")
        return False


def check_data_files():
    """Check if forensic evidence data files exist"""
    print("\n✓ Checking data files...")

    data_dir = Path(__file__).parent.parent.parent / "data"
    categories = ["credential_access", "execution", "lateral_movement", "network_logs"]

    if not data_dir.exists():
        print(f"  ✗ Data directory not found: {data_dir}")
        return False

    all_found = True
    for category in categories:
        category_dir = data_dir / category
        if category_dir.exists():
            files = list(category_dir.glob("*"))
            print(f"  ✓ {category}/ ({len(files)} files)")
        else:
            print(f"  ✗ {category}/ (NOT FOUND)")
            all_found = False

    return all_found


def check_config_file():
    """Check if configuration file exists"""
    print("\n✓ Checking configuration...", end=" ")

    config_file = Path(__file__).parent.parent.parent / "config" / "settings.yaml"

    if config_file.exists():
        print(f"✓ Configuration found")
        return True
    else:
        print(f"✗ Configuration file not found: {config_file}")
        return False


def check_project_structure():
    """Verify project directory structure"""
    print("\n✓ Checking project structure...")

    project_root = Path(__file__).parent.parent.parent
    required_dirs = ["src", "scripts", "config", "data"]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (NOT FOUND)")
            all_exist = False

    return all_exist


def main():
    """Run all validation checks"""
    print("=" * 70)
    print("TraceGuard AI - Setup Validation")
    print("=" * 70)

    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Configuration", check_config_file),
        ("Dependencies", check_dependencies),
        ("Data Files", check_data_files),
        ("Ollama Service", check_ollama_service),
    ]

    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n✗ Error during '{check_name}' check: {e}")
            results[check_name] = False

    # Summary
    print("\n" + "=" * 70)
    print("Validation Summary")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")

    print("=" * 70)
    print(f"Result: {passed}/{total} checks passed")

    if passed == total:
        print("\n✓ All checks passed! System is ready for investigation.\n")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please fix the issues above.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
