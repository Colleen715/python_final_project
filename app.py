from flask import Flask, render_template, request, flash, redirect, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
import hashlib
import pymysql
import numpy as np
import pandas as pd
import jieba.analyse
import logging

pymysql.install_as_MySQLdb()

engine = create_engine("mysql://root:123456@127.0.0.1/work?charset=utf8mb4")
dbsession = sessionmaker(bind=engine)
db = dbsession()

def load_data():
    df = pd.read_csv('考研调剂数据-3.09.csv', encoding='utf-8')
    df_info = pd.read_csv('大学信息_整理后.csv', encoding='utf-8')
    return df, df_info

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "as11sad"
    return app

app = create_app()


@app.route("/")
def home():
    return render_template('home.html')


@app.route('/login/', methods=["GET", "POST"])
def login():
    try:
        if request.method == "GET":
            session.clear()
            return render_template("login.html")
        name = request.form.get("name")
        password = request.form.get("password")
        if name == "":
            flash("用户名不能为空")
            return redirect(url_for('login'))
        if password == "":
            flash("密码不能为空")
            return redirect(url_for('login'))
        user = db.query(User).filter_by(name=name).all()
        if user == []:
            flash("该用户不存在，请先注册。")
            return redirect(url_for('login'))
        md5 = hashlib.md5()
        md5.update(password.encode("utf-8"))
        if md5.hexdigest() != user[0].password:
            flash("密码错误，请重新输入密码。")
            return redirect(url_for('login'))
        flash("登录成功！")
        session["id"] = user[0].id
        session["name"] = name

        app.logger.info('%s用户登录成功' % name)
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/index/', methods=["GET", "POST"])
def index():
    try:
        user_id = session.get("id")
        name = session.get("name")
        if name == None:
            return redirect(url_for('home'))
        df, df_info = load_data()
        df_info = df_info.drop_duplicates()  # 删除重
        df_2020 = df[df['time'].str.contains('2020')].copy()
        df_all = pd.merge(df_2020, df_info, how='left', on='school')
        df_all = df_all[['school', 'name', 'time', 'province', 'school_level', 'school_types']]
        level_perc = df_all.school_level.value_counts() / df_all.school_level.value_counts().sum()
        level_perc = np.round(level_perc * 100, 2)
        index = level_perc.index.tolist()
        data = level_perc.tolist()
        datas = []
        for k,v in zip(index, data):
            data_d = {}
            data_d["value"] = v
            data_d["name"] = k
            datas.append(data_d)
        print(datas)

        app.logger.info('%s用户进入主页' % name)
        return render_template('index.html', index=index, datas=datas)
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/register/', methods=["GET", "POST"])
def register():
    try:
        if request.method == "GET":

            return render_template('register.html')
        name = request.form.get("name")
        password = request.form.get("password")
        re_password = request.form.get("re_password")
        if name == "":
            flash("用户名不能为空")
            return redirect(url_for('register'))
        if password == "":
            flash("密码不能为空")
            return redirect(url_for('register'))
        if re_password == "":
            flash("确认密码不能为空")
            return redirect(url_for('register'))
        if len(password) <= 6 or len(password) >= 18:
            flash("密码长度必须大于6位小于18位")
            return redirect(url_for('register'))
        if password != re_password:
            flash("两次密码输入不一致")
            return redirect(url_for('register'))
        user = db.query(User).filter_by(name=name).all()
        if user != []:
            flash("改用户名已被占用")
            return redirect(url_for('register'))

        md5 = hashlib.md5()
        md5.update(password.encode("utf-8"))
        user = User(name=name, password=md5.hexdigest())
        db.add(user)
        db.commit()
        flash("注册成功!")
        app.logger.info('%s用户注册成功' % name)
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/logout/', methods=["GET", "POST"])
def logout():
    try:
        user_id = session["id"]
        name = session["name"]
        session.clear()
        flash("注销成功！")

        app.logger.info('%s用户注销成功' % name)
        return redirect(url_for('home'))
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/school_level/', methods=["GET", ])
def school_level():
    try:
        user_id = session.get("id")
        name = session.get("name")
        if name == None:
            return redirect(url_for('home'))
        app.logger.info('%s用户查看学校等级模块成功' % name)
        return render_template('index.html')
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/school_type/', methods=["GET", ])
def school_type():
    try:
        user_id = session.get("id")
        name = session.get("name")
        if name == None:
            return redirect(url_for('home'))
        df, df_info = load_data()
        df_info = df_info.drop_duplicates()  # 删除重
        df_2020 = df[df['time'].str.contains('2020')].copy()
        df_all = pd.merge(df_2020, df_info, how='left', on='school')
        df_all = df_all[['school', 'name', 'time', 'province', 'school_level', 'school_types']]
        type_perc = df_all.school_types.value_counts() / df_all.school_types.value_counts().sum()
        type_perc = np.round(type_perc * 100, 2)
        index = type_perc.index.tolist()
        data = type_perc.values.tolist()
        datas = []
        for k, v in zip(index, data):
            data_d = {}
            data_d["value"] = v
            data_d["name"] = k
            datas.append(data_d)
        print(datas)

        app.logger.info('%s用户查看学校类型模块成功' % name)
        return render_template('school_type.html', index=index, datas=datas)
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/num_dis_info/', methods=["GET", ])
def num_dis_info():
    try:
        user_id = session.get("id")
        user_name = session.get("name")
        if user_name == None:
            return redirect(url_for('home'))
        df, df_info = load_data()
        df_info = df_info.drop_duplicates()  # 删除重
        df_2020 = df[df['time'].str.contains('2020')].copy()
        df_all = pd.merge(df_2020, df_info, how='left', on='school')
        df_all = df_all[['school', 'name', 'time', 'province', 'school_level', 'school_types']]
        province_num = df_all.province.value_counts().sort_values()
        name = province_num.index.tolist()
        num = province_num.values.tolist()
        datas = []
        for k,v in zip(name, num):
            l = []
            l.append(v)
            l.append(k)
            datas.append(l)
        print(datas)

        app.logger.info('%s用户查看调剂信息发布数省份成功' % user_name)
        return render_template('num_dis_info.html', datas=datas)
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/time_chart/', methods=["GET", ])
def time_chart():
    try:
        user_id = session.get("id")
        name = session.get("name")
        if name == None:
            return redirect(url_for('home'))
        df, df_info = load_data()
        df_info = df_info.drop_duplicates()  # 删除重
        df_2020 = df[df['time'].str.contains('2020')].copy()
        df_all = pd.merge(df_2020, df_info, how='left', on='school')
        df_all = df_all[['school', 'name', 'time', 'province', 'school_level', 'school_types']]
        pub_time = df_all.time.value_counts().sort_index()
        datas = []
        for k,v in zip(pub_time.index.tolist(), pub_time.values.tolist()):
            d = {}
            d["time"] = k
            d["num"] = v
            datas.append(d)
        print(datas)
        app.logger.info('%s用户查看调剂信息发布时间走势成功' % name)
        return render_template('time_chart.html', datas=datas)
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)


@app.route('/word_cloud/', methods=["GET", ])
def word_coloud():
    try:
        user_id = session.get("id")
        name = session.get("name")
        if name == None:
            return redirect(url_for('home'))
        df, df_info = load_data()
        txt = df['name'].str.cat()
        # 添加关键词
        jieba.add_word('材料科学与工程')

        # 读入停用词表
        stop_words = []
        # with open('E:\py练习\数据分析\stop_words.txt','r',encoding='utf-8')as f:
        #     lines = f.readlines()
        #     for line in lines:
        #         stop_words.append(line.strip())

        # 添加停用词
        stop_words.extend(['查看', '详细', '详见', '详情', '与化', '03', '02', '01', '正文', '多个', '相关', '..'])
        # 字段分词处理
        word_num = jieba.analyse.extract_tags(txt,
                                              topK=100,
                                              withWeight=True,
                                              allowPOS=())
        # 去停用词
        word_num_selected = []
        for i in word_num:
            if i[0] not in stop_words:
                word_num_selected.append(i)

        key_words = pd.DataFrame(word_num_selected, columns=['words', 'num'])
        datas = []
        for k,v in zip(key_words.words.tolist(), key_words.num.tolist()):
            l = []
            l.append(k)
            l.append(v)
            datas.append(l)
        print(datas)

        app.logger.info('%s用户查看词云图成功' % name)
        return render_template('work_cloud.html', datas=datas)
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/map/', methods=["GET", ])
def map():
    try:
        user_id = session.get("id")
        user_name = session.get("name")
        if user_name == None:
            return redirect(url_for('home'))
        df, df_info = load_data()
        df_info = df_info.drop_duplicates()  # 删除重
        df_2020 = df[df['time'].str.contains('2020')].copy()
        df_all = pd.merge(df_2020, df_info, how='left', on='school')
        df_all = df_all[['school', 'name', 'time', 'province', 'school_level', 'school_types']]
        province_num = df_all.province.value_counts().sort_values()
        name = province_num.index.tolist()
        num = province_num.values.tolist()
        datas = []
        for k,v in zip(name, num):
            d = {}
            d["name"] = k
            d["value"] = v
            datas.append(d)
        print(datas)
        app.logger.info('%s用户查看地图成功' % user_name)
        return render_template('map.html', datas=datas)
    except Exception as e:
        app.logger.warning(e)
        app.logger.error(e)

@app.route('/log/')
def hello_world():
    with open(r'flask.log', 'r', encoding='utf-8') as f:
        data = f.readlines()
    datas = []
    for i in data:
        d = {}
        detail = i.split('-')
        d["time"] = detail[0] + "-" + detail[1] + "-" + detail[2]
        d["level"] = detail[3]
        d["function"] = detail[5]
        d["line"] = detail[6]
        d["message"] = detail[7][0:-1]
        print(d)
        datas.append(d)
    return render_template('log.html', datas=datas)


if __name__ == '__main__':
    app.debug = True
    handler = logging.FileHandler('flask.log', encoding='UTF-8')
    handler.setLevel(logging.INFO)  # 设置日志记录最低级别为DEBUG，低于DEBUG级别的日志记录会被忽略，不设置setLevel()则默认为NOTSET级别。
    logging_format = logging.Formatter(
        '%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s-%(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    app.run(host="0.0.0.0", debug=True)
