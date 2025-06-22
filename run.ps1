foreach ($i in 5, 10, 50, 100) {
    foreach ($j in 1, 5, 10) {
        $directoryName = "results_${i}_${j}"

        New-Item -ItemType Directory -Path $directoryName -Force | Out-Null
        python3 src/main.py 80 50 50 $i $j

    }
}
