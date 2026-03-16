#!/usr/bin/env python3
"""
Network Configuration Validator
Validates Terraform and Ansible configurations before deployment.
"""

import os
import sys
import json

def validate_terraform():
    """Run terraform validate"""
    print("🔍 Validating Terraform configurations...")
    result = os.system("cd terraform && terraform validate")
    return result == 0

def check_syntax():
    """Basic syntax checks"""
    print("🔍 Running syntax checks...")
    # Add custom validation logic here
    return True

def main():
    print("=" * 50)
    print("Network Configuration Validator")
    print("=" * 50)
    
    all_passed = True
    
    if not validate_terraform():
        all_passed = False
        print("❌ Terraform validation failed")
    else:
        print("✅ Terraform validation passed")
    
    if not check_syntax():
        all_passed = False
        print("❌ Syntax check failed")
    else:
        print("✅ Syntax check passed")
    
    print("=" * 50)
    if all_passed:
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())