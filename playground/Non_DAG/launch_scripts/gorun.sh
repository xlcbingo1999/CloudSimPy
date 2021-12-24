#!/bin/bash
echo "执行调度算法 $1"
time=$(date "+%Y%m%d-%H%M%S")
echo ${time}
if [ ! $1 ]; then
    python firstfit-makespan.py >> ./results/firstfit-makespan-${time}.log
elif [ "$1" = "random" ]; then
    python random-makespan.py >> ./results/random-makespan-${time}.log
elif [ "$1" = "firstfit" ]; then
    python firstfit-makespan.py >> ./results/firstfit-makespan-${time}.log
elif [ "$1" = "Tetris" ]; then
    python Tetris-makespan.py >> ./results/Tetris-makespan-${time}.log
elif [ "$1" = "DeepJS" ]; then
    python DeepJS-makespan.py >> ./results/DeepJS-makespan-${time}.log
else
    echo "匹配执行出错"
fi