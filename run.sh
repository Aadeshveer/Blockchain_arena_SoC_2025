for i in 5 10 50 100
do
    for j in 1 5 10
    do
        mkdir -p "results_"$i"_"$j
        Write-Host "Running simulation for average block mining interval=$i, transaction mean time =$j in directory $directoryName"
        python3 src/main.py 80 50 50 $i $j
    done
done