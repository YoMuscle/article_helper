#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recreate database
"""
import os
import sys

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Delete old database
if os.path.exists('apa_checker.db'):
    os.remove('apa_checker.db')
    print('[OK] Old database deleted')

# Recreate database
from app import app, db

with app.app_context():
    db.create_all()
    print('[OK] Database recreated successfully!')
    print('\nTables created:')
    print('- users (with theme_preference and is_premium)')
    print('- documents')
    print('- email_verifications')
    print('- password_resets')

