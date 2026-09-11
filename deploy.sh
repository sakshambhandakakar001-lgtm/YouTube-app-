#!/bin/bash
echo "Code update ho raha hai..."
git add .
git commit -m "Auto update via Termux script"
git push origin main
echo "GitHub par push ho gaya! Render par deployment shuru ho chuki hogi."
