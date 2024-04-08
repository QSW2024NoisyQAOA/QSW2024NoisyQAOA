QLM_RESOURCEMANAGER_CONFIG_FILE_PATH=/invalid/path python3 run_benchmarks.py \
    -v -r -o "results/fidelity" -P $1 --done_marker \
    -p "{metric:'fidelity',source:{model:[\
        {type:'noisy_composite', sx: true, time: 1, noise: 1},\
        {type:'noisy_composite', sx: true, noise: 0, time: 1},\
        {type:'noisy_composite', sx: true, noise:1, noise: 0}\
    ], algorithm:{type:['qaoa', 'wsqaoa','wsinitqaoa'],nLayers:[1,2,3]}},graphs:{problem:['partition', 'maxcut'],size:[5,6,7,8,9,10]}}" 