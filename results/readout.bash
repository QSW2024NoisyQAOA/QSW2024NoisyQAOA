QLM_RESOURCEMANAGER_CONFIG_FILE_PATH=/invalid/path python3 run_benchmarks.py \
    -v -r -o "results/readout" -P $1 --done_marker \
    -p "{metric:'approx_ratio',source:{model:{type:'noisy_composite', sx: true, readout: 1.0},
    algorithm:[{type:['qaoa','wsqaoa','wsinitqaoa'],nLayers:[1,2,3], nShots:3}, {type:'rqaoa', nSamples:10, nShots: 5, nLayers:[1,2,3]}]},\
    graphs:{problem: 'maxcut',size:[5,6,7,8,9,10]}}" 