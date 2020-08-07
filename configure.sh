#!/bin/bash

echo '' >> "$HOME"/.zshrc
echo '# multicrack:' >> "$HOME"/.zshrc
echo "alias multicrack='python3 /Users/emil/Desktop/github/multi_aircrack_tool/multicrack.py'" >> "$HOME"/.zshrc
source "$HOME"/.zshrc
echo Done!
