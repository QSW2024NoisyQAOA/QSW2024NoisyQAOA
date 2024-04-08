QLM_RESOURCEMANAGER_CONFIG_FILE_PATH=/invalid/path python3 run_benchmarks.py \
    -v -r -o "results/large_noise" -P $1 --done_marker \
    -p "{metric:'approx_ratio',source:{model:[\
        {type:'noisy_composite', noise: [2.0], time: [2.0], sx: true},\
        {type:'noisy_composite', noise: [3.0], time: [3.0], sx: true},\
        {type:'noisy_composite', noise: [4.0], time: [4.0], sx: true}\
    ], algorithm:[{type:['qaoa','wsqaoa','wsinitqaoa'],nLayers:[1,2,3], nShots:3}, {type:'rqaoa', nSamples: [10, 100, 1000, null], nShots: 5, nLayers:[1,2,3]}]},\
    graphs:{problem:['maxcut', 'partition'],size:[5,6,7,8,9,10]}}" 