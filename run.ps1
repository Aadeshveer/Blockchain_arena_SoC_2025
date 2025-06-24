foreach ($i in 5, 10, 50, 100) {
    foreach ($j in 1, 5, 10) {
        $directoryName = "results_${i}_${j}"
        Write-Host "Running simulation for average block mining interval=$i, transaction mean time =$j in directory $directoryName"
        python3 src/main.py 80 50 50 $i $j F

    }
}
