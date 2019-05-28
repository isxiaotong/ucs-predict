### 目录说明
- vc/date_gap: value_count()函数的输出txt及>2的画图 [来源自merge.py]


### 统计规律
- 每个用户都至少购买过一次
- 2月23日前7天购买用户人数异常
- user 数据分箱结果变差
- cart 最早出现日期 04-08 



### 特征

### 参考
- jdata 思路
```txt
https://blog.csdn.net/weixin_42182923/article/details/82432717
```
- jdata 代码
```txt    
https://github.com/hecongqing/2017-jdata-competition
https://github.com/foursking1/jd
https://zhuanlan.zhihu.com/p/26177617
```
- xgboost 调参    
```txt   
https://blog.csdn.net/mmc2015/article/details/51019894
https://xgboost.readthedocs.io/en/latest/parameter.html#general-parameters 
https://wuhuhu800.github.io/2018/02/28/xgboost_parameters/
https://blog.csdn.net/han_xiaoyang/article/details/52665396
https://blog.csdn.net/SzM21C11U68n04vdcLmJ/article/details/78516866
```

- xgboost 官方文档
```txt    
https://xgboost.readthedocs.io/en/latest/python/python_intro.html
```

- xgboost 代码
```txt    
https://github.com/dmlc/xgboost/tree/master/demo/guide-python
https://github.com/dmlc/xgboost/tree/master/tests/python
https://zhuanlan.zhihu.com/p/31182879
```

- python画图
```txt    
https://matplotlib.org/gallery/index.html
https://seaborn.pydata.org/tutorial.html
http://liyangbit.com/pythonvisualization/matplotlib-top-50-visualizations/#20-%E8%BF%9E%E7%BB%AD%E5%8F%98%E9%87%8F%E7%9A%84%E7%9B%B4%E6%96%B9%E5%9B%BE-histogram-for-continuous-variable
```

- pandas大数据
```txt    
https://blog.csdn.net/weiyongle1996/article/details/78498603
```

- pandas参数
```txt    
https://blog.csdn.net/u010801439/article/details/80033341
```

- pandas报错
```txt    
https://zhuanlan.zhihu.com/p/41202576
```

- 样本不平衡
```txt    
https://blog.csdn.net/pearl8899/article/details/80820067
https://blog.csdn.net/u012735708/article/details/82877501
```

### 环境
```txt
certifi==2019.3.9
chardet==3.0.4
cycler==0.10.0
docopt==0.6.2
idna==2.8
kiwisolver==1.1.0
matplotlib==3.0.3
numpy==1.16.3
pandas==0.24.2
pyparsing==2.4.0
python-dateutil==2.8.0
pytz==2019.1
requests==2.21.0
scikit-learn==0.20.3
scipy==1.2.1
six==1.12.0
urllib3==1.24.3
wincertstore==0.2
xgboost==0.82
yarg==0.1.9
```