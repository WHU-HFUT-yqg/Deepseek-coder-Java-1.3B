# Deepseek-coder-Java-1.3B
A project filter the data to train the model so that can improve the ablity of Fill the blank in Java

#How to fillter and create the FIM Java Data

1.prepare your source data path
2.prepare your output_path

#reproduce and create your Java FIM train data
`cd data
python new_process_data.py --input_path /path/to/your/input_data --output_path /path/to/your/output_file.json --cache_dir /path/to/cache_dir --max_samples_per_code 3`
