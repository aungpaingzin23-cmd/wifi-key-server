#!/bin/bash
# ============================================================
# WiFi Bypass - Auto Setup & Compile (.so)
# Works on ANY Android phone with Termux
# Just paste this and run!
# ============================================================

clear
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   WiFi Bypass - Auto Setup           ║"
echo "  ║   Compile to .so (Protected)         ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Step 1: Install Termux packages
echo "[*] Step 1: Installing packages..."
pkg update -y > /dev/null 2>&1
pkg upgrade -y > /dev/null 2>&1
pkg install python clang git -y > /dev/null 2>&1

# Step 2: Install Cython
echo "[*] Step 2: Installing Cython..."
pip install cython --break-system-packages 2>/dev/null || pip install cython 2>/dev/null

# Step 3: Create setup.py for compilation
echo "[*] Step 3: Compiling to .so ..."

cat > setup.py << 'PYEOF'
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize(
        "scan_keyed.py",
        compiler_directives={
            "binding": True,
            "embedsignature": True,
        }
    )
)
PYEOF

# Step 4: Build .so
python3 setup.py build_ext --inplace 2>&1 | grep -E "(error|Success|copying|\.so)" 

# Step 5: Clean up source
echo ""
if ls scan_keyed*.so 1>/dev/null 2>&1; then
    SO_FILE=$(ls scan_keyed*.so)
    echo "=========================================="
    echo "  ✅ COMPILE SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "  📁 File: $SO_FILE"
    echo "  📏 Size: $(du -h $SO_FILE | cut -f1)"
    echo ""
    echo "=========================================="
    echo "  🚀 TO RUN:"
    echo "  python3 -c 'import scan_keyed'"
    echo "=========================================="
    echo ""
    
    # Clean up unnecessary files
    rm -f scan_keyed.py scan_keyed.c setup.py
    rm -rf build/
    echo "[*] Source files cleaned up (scan_keyed.py removed)"
else
    echo "  ❌ COMPILE FAILED!"
    echo "  [!] Make sure all dependencies are installed."
    echo "  [!] Try: pkg install python clang && pip install cython"
fi
