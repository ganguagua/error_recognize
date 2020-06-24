
if [ ! -d "./chinese_L-12_H-768_A-12" ]; then
    wget https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip
    unzip chinese_L-12_H-768_A-12.zip
fi

export BERT_BASE_DIR=./chinese_L-12_H-768_A-12
export GLUE_DIR=./data

python run_classifier.py \
  --task_name=correct \
  --do_train=true \
  --do_eval=false \
  --do_predict=false \
  --data_dir=./data \
  --vocab_file=$BERT_BASE_DIR/vocab.txt \
  --bert_config_file=$BERT_BASE_DIR/bert_config.json \
  --init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt \
  --max_seq_length=50 \
  --train_batch_size=32 \
  --learning_rate=2e-5 \
  --num_train_epochs=1 \
  --output_dir=./output/
