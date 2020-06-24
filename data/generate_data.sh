
set -e

python convert_html.py samples > tmp
python ../get_sentences.py tmp > standard
cat standard|sort|uniq > tmp
mv tmp standard
python3 ../generate_error.py standard > error
awk -F '\t' '{if(length($1)<50) print $1"\t-1"}' standard > train.tsv
cat error|grep -v UNK|awk -F '\t' '{if(length($1)<50&&$2>=0) print $0}' >> train.tsv
python mix.py train.tsv > tmp
mv tmp train.tsv
