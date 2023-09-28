#!/bin/bash


#Schülerbücherrei
domain="localhost:5000"

# Use ping to check if the domain is reachable
curl "$domain" > /dev/null 2>&1

# Check the exit status of the ping command
if [ $? -eq 0 ]; then
    echo "Library-Software is online"
else
    echo "Starting Library-Software"
    cd library-software
    nohup python3 app.py &
    cd ..
fi



#LMB-Software
domain="localhost:5100"

# Use ping to check if the domain is reachable
curl "$domain" > /dev/null 2>&1

# Check the exit status of the ping command
if [ $? -eq 0 ]; then
    echo "School-Book-Managment-Software is online"
else
    echo "Starting School-Book-Managment-Software"
    cd school-book-managment-software
    nohup python3 main.py &
fi

echo "Finished"