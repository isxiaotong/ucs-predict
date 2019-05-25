# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @DATE    : 5/14/2019
# @Author  : xiaotong niu
# @File    : us_xgb.py
# @Project : JData-Predict
# @Github  ：https://github.com/isNxt
# @Describ : ...

import os
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
import lightgbm as lgb
from sklearn.model_selection import train_test_split

from merg_us import gen_feat
from s_feat import feat_buy_plus

# %% 配置
# 输出设置
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
plt.rcParams['figure.figsize'] = (12, 8)

# 时间划分
data_start_date = "2018-02-01"
data_end_date = "2018-04-15"

# 文件列表
ori_list = ['jdata_action.csv', 'jdata_user.csv', 'jdata_product.csv', 'jdata_shop.csv', 'jdata_comment.csv']
fill_list = ['jdata_user.csv', 'jdata_shop.csv']
clean_list = ['action.csv', 'user.csv', 'product.csv', 'shop.csv', 'comment.csv']

# 路径
data_path = "../data"
ori_path = "../data/ori"
clean_path = "../data/clean"
fill_path = "../data/fill"
user_path = clean_path + "/user.csv"
action_path = clean_path + "/action.csv"
product_path = clean_path + "/product.csv"
shop_path = clean_path + "/shop.csv"
submit_path = '../submit'
cache_path = '../cache'


# %% xgboost模型
def impt_feat(df_train, drop_column):
    """ back 重要性
    """
    dump_path = './lgb/bst.model'
    if os.path.exists(dump_path):
        # 获取特征
        print(datetime.now())
        print('>> 开始特征重要性')
        feat_cols = (df_train.drop(drop_column, axis=1)).columns
        print('<< 完成特征重要性')
        # 测试模型
        bst = xgb.Booster(model_file=dump_path)
        f_score = bst.get_fscore()
        f_name = []
        for id in list(f_score.keys()):
            f_name.append(feat_cols[int(id[1:])])
        f_id = pd.DataFrame({'f_id': list(f_score.keys())})
        f_pro = pd.DataFrame({'f_pro': list(f_score.values())})
        f_name = pd.DataFrame({'f_name': f_name})
        f_score = pd.concat([f_id, f_name, f_pro], axis=1)
        f_score.sort_values(by=['f_pro'], ascending=[0], inplace=True)
        f_score.to_csv('./lgb/impt_feat.csv', index=False)


def report(real, pred):
    print('real:', real.shape)
    # print(real.head())
    print('pred:', pred.shape)
    # print(pred.head())

    # 所有购买用户品类
    all_2 = real[['user_id', 'cate']]
    print('all_2:', all_2.shape)
    # 所有预测购买用户品类
    all_pred_2 = pred[['user_id', 'cate']]
    print('all_pred_2:', all_pred_2.shape)
    # 计算所有用户品类购买评价指标
    intersect = pd.merge(all_2, all_pred_2, how='inner')
    pos = intersect.shape[0]
    neg = all_pred_2.shape[0] - pos
    print('pos:', pos)
    print('neg:', neg)
    all_2_acc = 1.0 * pos / (pos + neg)
    all_2_recall = 1.0 * pos / len(all_2)
    print('所有用户品类中预测购买用户品类的准确率为 ' + str(all_2_acc))
    print('所有用户品类中预测购买用户品类的召回率' + str(all_2_recall))
    F11 = 3.0 * all_2_recall * all_2_acc / (2.0 * all_2_recall + all_2_acc)
    print('F11=' + str(F11))

    # 所有用户品类店铺对
    all_3 = real[['user_id', 'cate', 'shop_id']]
    print('all_3:', all_3.shape)
    # 所有预测用户品类店铺对
    all_pred_3 = pred[['user_id', 'cate', 'shop_id']]
    print('all_pred_3:', all_pred_3.shape)
    intersect = pd.merge(all_3, all_pred_3, how='inner')
    pos = intersect.shape[0]
    neg = all_pred_2.shape[0] - pos
    print('pos:', pos)
    print('neg:', neg)
    all_3_acc = 1.0 * pos / (pos + neg)
    all_3_recall = 1.0 * pos / len(all_3)
    print('所有用户品类中预测购买店铺的准确率为 ' + str(all_3_acc))
    print('所有用户品类中预测购买店铺的召回率' + str(all_3_recall))
    F12 = 5.0 * all_3_acc * all_3_recall / (2.0 * all_3_recall + 3.0 * all_3_acc)
    print('F12=' + str(F12))

    score = 0.4 * F11 + 0.6 * F12
    print('score=' + str(score))


def bst_param(df_train, df_test,drop_column):

    """ 构造
     xgboost模型训练测试
     """
    print('\n>> 开始划分X,y')
    X_train = df_train.drop(drop_column, axis=1).values
    y_train = df_train['label'].values
    X_test = df_test.drop(drop_column, axis=1).values
    y_test = df_test['label'].values
    print('<< 完成划分X,y')

    print(datetime.now())
    print('\n>> 开始优化参数')
    train = lgb.Dataset(X_train, y_train)
    valid = lgb.Dataset(X_test, y_test, reference=train)

    parameters = {
        'max_depth': [15, 20, 25, 30, 35],
        'learning_rate': [0.01, 0.02, 0.05, 0.1, 0.15],
        'feature_fraction': [0.6, 0.7, 0.8, 0.9, 0.95],
        'bagging_fraction': [0.6, 0.7, 0.8, 0.9, 0.95],
        'bagging_freq': [2, 4, 5, 6, 8],
        'lambda_l1': [0, 0.1, 0.4, 0.5, 0.6],
        'lambda_l2': [0, 10, 15, 35, 40],
        'cat_smooth': [1, 10, 15, 20, 35]
    }
    gbm = lgb.LGBMClassifier(boosting_type='gbdt',
                             objective='binary',
                             metric='auc',
                             verbose=0,
                             learning_rate=0.01,
                             num_leaves=35,
                             feature_fraction=0.8,
                             bagging_fraction=0.9,
                             bagging_freq=8,
                             lambda_l1=0.6,
                             lambda_l2=0)
    # 有了gridsearch我们便不需要fit函数
    gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
    gsearch.fit(X_train, y_train)

    print("Best score: %0.3f" % gsearch.best_score_)
    print("Best parameters set:")
    best_parameters = gsearch.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))


def model(df_train, df_test, drop_column):
    """ 构造
    xgboost模型训练测试
    """

    dump_path = './lgb/bst.model'
    if os.path.exists(dump_path):
        # 划分(X,y)
        print(datetime.now())
        print('\n>> 开始加载已有模型')
        bst = xgb.Booster(model_file=dump_path)
    else:
        # 划分(X,y)
        print(datetime.now())
        print('\n>> 开始划分X,y')
        X_train = df_train.drop(drop_column, axis=1).values
        y_train = df_train['label'].values
        X_test = df_test.drop(drop_column, axis=1).values
        y_test = df_test['label'].values
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        print('<< 完成划分X,y')
        # 设置参数(gridcv最佳)
        print(datetime.now())
        print('\n>> 开始设置参数')
        weight = (len(y_train) - np.sum(y_train)) / (np.sum(y_train))
        param = {
            # 默认
            'silent': 0,
            'objective': 'binary:logistic',
            'scale_pos_weight': 1,
            # 调整
            'learning_rate': 0.1,
            'n_estimators': 1000,
            'max_depth': 3,
            'min_child_weight': 5,
            'gamma': 0,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'eta': 0.05,
        }
        plst = list(param.items())
        plst += [('eval_metric', 'auc')]  # auc logloss
        num_round = 500
        evallist = [(dtest, 'eval'), (dtrain, 'train')]
        print('<< 完成设置参数')

        # 训练模型(watchlist)
        print(datetime.now())
        print('\n>> 开始训练模型')
        bst = xgb.train(plst, dtrain, num_round, evallist, early_stopping_rounds=50)
        bst.save_model("./lgb/bst.model")
        print('<< 完成训练模型')

    # 划分(X,y)
    print(datetime.now())
    print('\n>> 开始划分X,y')
    X_test = df_test.drop(drop_column, axis=1).values
    y_test = df_test['label'].values
    dtest = xgb.DMatrix(X_test)
    print('<< 完成划分X,y')

    # 测试模型
    print('\n>> 开始测试模型')
    y_probab = bst.predict(dtest)
    print('> 概率转换0,1')
    df_pred = pd.concat([df_test, pd.DataFrame({'probab': y_probab, 'pred': [0] * len(y_probab)})], axis=1)
    del df_train, df_test
    df_pred.sort_values(by='probab', ascending=False, inplace=True)
    df_pred.drop_duplicates(['user_id', 'cate'], keep='first', inplace=True)
    df_pred.reset_index(drop=True, inplace=True)
    product = pd.read_csv(product_path, na_filter=False)[['sku_id', 'shop_id']]
    df_pred = pd.merge(df_pred, product, on='sku_id', how='left')
    # df_pred.to_csv('./lgb/test_pred.csv', index=False)

    # 计算得分
    print('\n>> 开始计算得分')
    dump_path = cache_path + '/test_real.csv'
    if os.path.exists(dump_path):
        # 划分(X,y)
        print(datetime.now())
        df_real = pd.read_csv(dump_path)
    else:
        end_date = datetime.strptime('2018-4-1', '%Y-%m-%d')
        df_real = feat_buy_plus(end_date + timedelta(days=1), end_date + timedelta(days=7))[
            ['user_id', 'cate', 'shop_id']]
        df_real = df_real.drop_duplicates(['user_id', 'cate'])
        df_real.to_csv(dump_path, index=False)

    df_pred = df_pred[['user_id', 'cate', 'shop_id', 'pred']]
    print('前%s行[test] label=1：' % (str(df_real.shape[0])))
    report(df_real, df_pred.iloc[:df_real.shape[0]])

    for amt in range(160000, 250000, 10000):
        print('前%s行 label=1：' % (str(amt)))
        report(df_real, df_pred.iloc[:amt])
    print('<< 完成测试模型')


def submit(df_sub, drop_column):
    """
    xgboost模型提交
    """
    dump_path = './lgb/bst.model'
    if os.path.exists(dump_path):
        # 划分(X,y)
        print(datetime.now())
        print('>> 开始划分X,y')
        X_sub = df_sub.drop(drop_column, axis=1).values
        print('<< 完成划分数据')

        # 预测提交
        print('>> 开始预测提交')
        dsub = xgb.DMatrix(X_sub)
        # dsub.save_binary('./lgb/dsub.buffer')
        bst = xgb.Booster(model_file=dump_path)
        y_probab = bst.predict(dsub)
        print('> 概率转换0,1')
        df_pred = pd.concat([df_sub, pd.DataFrame({'probab': y_probab, 'pred': [0] * len(y_probab)})], axis=1)
        df_pred = df_pred.sort_values(by='probab', ascending=False)
        df_pred = df_pred.drop_duplicates(['user_id', 'cate'], keep='first')
        df_pred = df_pred.reset_index(drop=True)
        product = pd.read_csv(product_path, na_filter=False)[['sku_id', 'shop_id']]
        df_pred = pd.merge(df_pred, product, on='sku_id', how='left')

        df_pred.ix[:10000, 'pred'] = 1
        df_pred.to_csv('./lgb/sub_pred.csv', index=False)
        # 格式化提交
        df_pred = df_pred[df_pred['pred'] == 1]
        df_pred = df_pred[['user_id', 'cate', 'shop_id']]
        df_pred.to_csv(submit_path + '/us.csv', index=False)
        print('> 提交结果', df_pred.shape)
        print('<< 完成预测提交!')
    else:
        print('<< 没有训练模型')


def main():
    """
    主流程
    """
    # 定义参数
    time_gap = [1, 2, 3, 7, 14]
    train_end_date = '2018-4-8'
    test_end_date = '2018-4-1'
    sub_end_date = '2018-4-15'
    drop_column = ['user_id', 'sku_id', 'label']
    label_gap = 3  # [2,3,7]

    # 生成特征
    df_train = gen_feat(train_end_date, time_gap, label_gap, 'train')
    df_test = gen_feat(test_end_date, time_gap, label_gap, 'test')
    # df_sub = gen_feat(sub_end_date, time_gap, label_gap, 'submit')

    # Onehot编码

    # 优化参数
    bst_param(df_train, df_test, drop_column)

    # 构造模型
    # model(df_train, df_test, drop_column)
    # impt_feat(df_train, drop_column)

    # 生成提交结果
    # submit(df_sub, drop_column)


if __name__ == "__main__":
    main()