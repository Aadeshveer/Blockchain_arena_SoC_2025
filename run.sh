for i in 5 10 50 100
do
    for j in 1 5 10
    do
        python3 src/simulator/main.py 80 50 50 $i $j F
    done
done