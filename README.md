A project filter the data to train the model so that can improve the ablity of Fill the blank in Java

#### \#How to fillter and create the FIM Java Data

1.prepare your source data path 

2.prepare your output_path

#### \#reproduce and create your Java FIM train data 

```
conda create --name Deepseek-coder-Java-1.3B
conda activate Deepseek-coder-Java-1.3B

cd data
python data/new_process_data.py --input_path /path/to/your/input_data --output_path /path/to/your/output_file.json --cache_dir /path/to/cache_dir --max_samples_per_code 3
```

The final data will be created as an Alpaca format so that you can train  your own model with this.



#### #How to train

Our project use the LLama Factory to finetune the  base model Deepseek-coder-1.3B.

if you want to reproduce our experiments,you need to install the LLama Factory

```
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]" --no-build-isolation
```

train the model 

```
llamafactory-cli deepseek-coder-1.3B_lora_sft.yaml
```



