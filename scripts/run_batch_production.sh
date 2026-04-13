#!/bin/bash

# Reel 1: Inventory
./venv/bin/python main.py --preset royal_chic --upload --direct "Inventory errors stealing your time? Manual counts lead to chaos and wasted hours. Sound familiar? What if I told you custom AI trackers cut errors by 35%? Before, you were blind to errors. Now, real-time alerts keep you in control. DM 'INVENTORY' for a quick review of how this works for you." > generation_batch_1.log 2>&1

# Reel 2: Sync
./venv/bin/python main.py --preset royal_chic --upload --direct "Wasting hours on data issues? Manual data entry is costing you time and accuracy. With a simple AI agent, bridge your favorite tools seamlessly. Our users report a 30% boost in efficiency and 90% fewer errors. DM 'SYNC' to learn how to start today!" > generation_batch_2.log 2>&1

# Reel 3: Report
./venv/bin/python main.py --preset royal_chic --upload --direct "Reports taking hours? Let’s cut that to minutes. Imagine pulling data into custom views—automatically. We set it up collaboratively, ensuring accuracy right off the bat. Users report a 30% decrease in errors—and major time savings. Comment 'REPORT' below to get this workflow for yourself." > generation_batch_3.log 2>&1
