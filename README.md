# error_recognize
基于弱监督训练的中文错别字识别，只需加入正确的文本就行，例如人民日报、新华社这种置信度高的

# 运行方式
#python3+tensorflow1.14
```
cd data && sh generate_data.sh && cd .. && sh run.sh
```
#如果有提示python包问题，自行pip install即可

# 数据
只需把正确文本按行放到./data/samples文件即可，程序会自动分句并生成错误文本
基于正确文本随机生成错别字，保证同音字、近音字、常见字、词组出现的频率更高，更接近真实的错误

# 模型
- 用了千万级别的数据，识别正式文章效果比较好。专有名词，新词易误报，加入相关的数据就能改善。
- 训练好的模型下载使用参见[https://blog.csdn.net/weixin_39422563/article/details/106957654](https://blog.csdn.net/weixin_39422563/article/details/106957654)
