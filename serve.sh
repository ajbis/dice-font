#!/bin/bash
cd "$(dirname "$0")/dist"
python3 -m http.server 8000 &
echo "Serving at http://localhost:8000"
xdg-open "http://localhost:8000" 2>/dev/null || open "http://localhost:8000" 2>/dev/null
