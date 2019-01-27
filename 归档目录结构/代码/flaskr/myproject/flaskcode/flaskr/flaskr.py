# -*- coding: utf-8 -*-

import sys
import os
import datetime
import chardet
from flask import Flask, render_template, session, redirect, url_for, flash, request, send_from_directory
from werkzeug import secure_filename
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
# from flask.ext.influxdb import InfluxDB
# from datetime import datetime
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from influxdb import InfluxDBClient

reload(sys)
sys.setdefaultencoding('utf8')

list_coeff = []
list_coeff_ex = []
list_cal = []
list_cal_ex = []
list_raw = []
list_raw_ex = []


UPLOAD_FOLDER = '/home/rosyphoton/myproject/flaskcode/flaskr/uploadfiles'
# ALLOWED_EXTENSIONS = set(
#     ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'rar', 'zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'hard to guess string'
client = InfluxDBClient('localhost', 8086, 'root', '', '')

bootstrap = Bootstrap(app)
moment = Moment(app)
# influx_db = InfluxDB(app)


class DateForm(Form):                                                                   #日期类
    date = StringField('请以如下格式输入日期："xxxx-xx-xx"', validators=[Required()])
    submit = SubmitField('Submit')

class QueryForm(Form):                                                                  #查询语句类
    database = StringField('请输入数据库名', validators=[Required()])
    queryinput = StringField('请输入查询语句', validators=[Required()])
    submit = SubmitField('Submit')

class RemarkForm(Form):                                                                 #备注类
    remark = StringField('请输入文件备注', validators=[Required()])
    submit = SubmitField('Submit')



# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# ----------------------------存储函数1---------------------------------

def store_func1(lines, filename, remark):                                               #类型一数据存储函数，存入formaldb数据库
    client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')                  #数据全部存入data_type_1表中
    for line in lines:
        time_x1 = line[0] + ' ' + line[1]
        latitude_x1 = line[2]
        longitude_x1 = line[3]
        height_x1 = line[4]
        component_x1 = float(line[5])
        component_y1 = float(line[6])
        component_z1 = float(line[7])
        field_channel1 = float(line[8])
        field_channel2 = float(line[9])

        json_body_1 = [
            {
                "measurement": "data_type_1",
                "tags": {
                    "num": "1",
                    "x_axis_component": component_x1,
                    "y_axis_component": component_y1,
                    "z_axis_component": component_z1,
                    "channel_1_total_field": field_channel1,
                    "channel_2_total_field": field_channel2,
                    "filename": filename
                },
                "time": time_x1,
                "fields": {
                    "latitude": latitude_x1,
                    "longitude": longitude_x1,
                    "height": height_x1,
                    "remark": remark
                }
            }
        ]

        client.write_points(json_body_1)                                                #数据以json格式写入数据库

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')                   #存储类型一数据同时将相关信息存入message数据库
    json_body = [
        {
            "measurement": "filename_filetype",
            "tags": {
                "filename": filename,
                "num": "1"
            },
            "fields": {
                "remark": remark
            }
        }
    ]
    client.write_points(json_body)
    # result = client.query('select * from data_type_1')
    # result_new = list(result.get_points())

# ---------------------------存储函数1-----------------------------



# ---------------------------存储函数2------------------------------

def store_func2(lines, filename, date, remark):                                         #类型二数据存储函数，存入formaldb数据库
    client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')                  #数据全部存入data_type_2表中
    for line in lines:
        dimension = len(line)
        scan_number = line[0]
        input_tags = line[1]
        component_x2 = float(line[2])
        component_y2 = float(line[3])
        component_z2 = float(line[4])

        if dimension >= 27:                                                             #总场数据组数为4的情况
            raw_mag1 = float(line[5])
            raw_mag2 = float(line[6])
            raw_mag3 = float(line[7])
            raw_mag4 = float(line[8])

            diff_mag1 = float(line[9])
            diff_mag2 = float(line[10])
            diff_mag3 = float(line[11])
            diff_mag4 = float(line[12])

            uncomp_mag1 = float(line[13])
            uncomp_mag2 = float(line[14])
            uncomp_mag3 = float(line[15])
            uncomp_mag4 = float(line[16])

            comp_mag1 = float(line[17])
            comp_mag2 = float(line[18])
            comp_mag3 = float(line[19])
            comp_mag4 = float(line[20])

            uncomp_grad1 = float(line[21])
            uncomp_grad2 = float(line[22])
            uncomp_grad3 = float(line[23])

            comp_grad1 = float(line[24])
            comp_grad2 = float(line[25])
            comp_grad3 = float(line[26])

            time_y2 = date + ' ' + line[27]                                             #类型二数据的时间需要加上存储时输入的日期

            json_body_2 = [
                {
                    "measurement": "data_type_2",
                    "tags": {
                        "num": "2",
                        "Fiducial_number": scan_number,
                        "Event_input_tags": input_tags,
                        "Grad_1_uncomp": uncomp_grad1,
                        "Grad_2_uncomp": uncomp_grad2,
                        "Grad_3_uncomp": uncomp_grad3,
                        "Grad_1_comp": comp_grad1,
                        "Grad_2_comp": comp_grad2,
                        "Grad_3_comp": comp_grad3,
                        "filename": filename
                    },
                    "time": time_y2,
                    "fields": {
                        "x_axis_component": component_x2,
                        "y_axis_component": component_y2,
                        "z_axis_component": component_z2,
                        "Mag_1_raw_TF": raw_mag1,
                        "Mag_2_raw_TF": raw_mag2,
                        "Mag_3_raw_TF": raw_mag3,
                        "Mag_4_raw_TF": raw_mag4,
                        "fourth_Diff_Mag_1_raw_TF": diff_mag1,
                        "fourth_Diff_Mag_2_raw_TF": diff_mag2,
                        "fourth_Diff_Mag_3_raw_TF": diff_mag3,
                        "fourth_Diff_Mag_4_raw_TF": diff_mag4,
                        "Mag_1_TF_uncomp": uncomp_mag1,
                        "Mag_2_TF_uncomp": uncomp_mag2,
                        "Mag_3_TF_uncomp": uncomp_mag3,
                        "Mag_4_TF_uncomp": uncomp_mag4,
                        "Mag_1_TF_comp": comp_mag1,
                        "Mag_2_TF_comp": comp_mag2,
                        "Mag_3_TF_comp": comp_mag3,
                        "Mag_4_TF_comp": comp_mag4,
                        "remark": remark
                    }
                }
            ]

        elif dimension >= 21:                                                           #总场数据组数为3的情况
            raw_mag1 = float(line[5])
            raw_mag2 = float(line[6])
            raw_mag3 = float(line[7])

            diff_mag1 = float(line[8])
            diff_mag2 = float(line[9])
            diff_mag3 = float(line[10])

            uncomp_mag1 = float(line[11])
            uncomp_mag2 = float(line[12])
            uncomp_mag3 = float(line[13])

            comp_mag1 = float(line[14])
            comp_mag2 = float(line[15])
            comp_mag3 = float(line[16])

            uncomp_grad1 = float(line[17])
            uncomp_grad2 = float(line[18])

            comp_grad1 = float(line[19])
            comp_grad2 = float(line[20])
            
            time_y2 = date + ' ' + line[21]
            
            json_body_2 = [
                {
                    "measurement": "data_type_2",
                    "tags": {
                        "num": "2",
                        "Fiducial_number": scan_number,
                        "Event_input_tags": input_tags,
                        "Grad_1_uncomp": uncomp_grad1,
                        "Grad_2_uncomp": uncomp_grad2,
                        "Grad_1_comp": comp_grad1,
                        "Grad_2_comp": comp_grad2,
                        "filename": filename
                    },
                    "time": time_y2,
                    "fields": {
                        "x_axis_component": component_x2,
                        "y_axis_component": component_y2,
                        "z_axis_component": component_z2,
                        "Mag_1_raw_TF": raw_mag1,
                        "Mag_2_raw_TF": raw_mag2,
                        "Mag_3_raw_TF": raw_mag3,
                        "fourth_Diff_Mag_1_raw_TF": diff_mag1,
                        "fourth_Diff_Mag_2_raw_TF": diff_mag2,
                        "fourth_Diff_Mag_3_raw_TF": diff_mag3,
                        "Mag_1_TF_uncomp": uncomp_mag1,
                        "Mag_2_TF_uncomp": uncomp_mag2,
                        "Mag_3_TF_uncomp": uncomp_mag3,
                        "Mag_1_TF_comp": comp_mag1,
                        "Mag_2_TF_comp": comp_mag2,
                        "Mag_3_TF_comp": comp_mag3,
                        "remark": remark
                    }
                }
            ]

        else:                                                                           #其他情况，即总场数据组数为2的情况
            raw_mag1 = float(line[5])
            raw_mag2 = float(line[6])

            diff_mag1 = float(line[7])
            diff_mag2 = float(line[8])

            uncomp_mag1 = float(line[9])
            uncomp_mag2 = float(line[10])

            comp_mag1 = float(line[11])
            comp_mag2 = float(line[12])

            uncomp_grad1 = float(line[13])

            comp_grad1 = float(line[14])
            
            time_y2 = date + ' ' + line[15]

            json_body_2 = [
                {
                    "measurement": "data_type_2",
                    "tags": {
                        "num": "2",
                        "Fiducial_number": scan_number,
                        "Event_input_tags": input_tags,
                        "Grad_1_uncomp": uncomp_grad1,
                        "Grad_1_comp": comp_grad1,
                        "filename": filename
                    },
                    "time": time_y2,
                    "fields": {
                        "x_axis_component": component_x2,
                        "y_axis_component": component_y2,
                        "z_axis_component": component_z2,
                        "Mag_1_raw_TF": raw_mag1,
                        "Mag_2_raw_TF": raw_mag2,
                        "fourth_Diff_Mag_1_raw_TF": diff_mag1,
                        "fourth_Diff_Mag_2_raw_TF": diff_mag2,
                        "Mag_1_TF_uncomp": uncomp_mag1,
                        "Mag_2_TF_uncomp": uncomp_mag2,
                        "Mag_1_TF_comp": comp_mag1,
                        "Mag_2_TF_comp": comp_mag2,
                        "remark": remark
                    }
                }
            ]

        client.write_points(json_body_2)


    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')                   #存储类型二数据同时将相关信息存入message数据库
    json_body = [
        {
            "measurement": "filename_filetype",
            "tags": {
                "filename": filename,
                "num": "2"
            },
            "fields": {
                "remark": remark
            }
        }
    ]
    client.write_points(json_body)
    # result = client.query("select * from data_type_2")
    # result_new = list(result.get_points())

# --------------------------存储函数2--------------------------



#------------------------文件内容格式转化函数----------------------

def fileDeal(filename, list_xxx, flag):                                                 #对读取的文件内容进行格式转化和处理
    lines_plus = []

    for list_unit in list_xxx:
        f = open(list_unit, "r")
        lines = f.readlines()
        # print lines
        lines_plus.append(lines)
        f.close()

    dimension = len(lines_plus[0])

    filetime = datetime.datetime.strptime(filename, "%m-%d-%Y%H-%M-%S")                 #将文件中的而时间格式转化为统一的标准格式
    finaltime = filetime.strftime(
        "%Y-%m-%d %H:%M:%S.") + filetime.strftime("%f")
    if flag == 'coeff':
        for i in range(0, dimension):
            line_new = [finaltime]
            filetime = filetime + datetime.timedelta(seconds=0.1)                       #根据文件中数据测量的起始时间，间隔0.1s计算每条数据流的时间
            finaltime = filetime.strftime(
                "%Y-%m-%d %H:%M:%S.") + filetime.strftime("%f")

            for line in lines_plus:                                                     #依次读取每个文件中的对应行的数据组合成一组标准格式测量数据
                line_new.append(line[i][:-2])
            list_coeff_ex.append(line_new)

    elif flag == 'cal':
        for i in range(0, dimension):
            line_new = [finaltime]
            filetime = filetime + datetime.timedelta(seconds=0.1)
            finaltime = filetime.strftime(
                "%Y-%m-%d %H:%M:%S.") + filetime.strftime("%f")

            for line in lines_plus:
                line_new.append(line[i][:-2])
            list_cal_ex.append(line_new)

    else:
        for i in range(0, dimension):
            line_new = [finaltime]
            filetime = filetime + datetime.timedelta(seconds=0.1)
            finaltime = filetime.strftime(
                "%Y-%m-%d %H:%M:%S.") + filetime.strftime("%f")

            for line in lines_plus:
                line_new.append(line[i][:-2])
            list_raw_ex.append(line_new)

#------------------------文件内容格式转化函数----------------------



#---------------------文件读取函数--------------------------

def eachFile(filename):
    pathDir = os.listdir(UPLOAD_FOLDER + "/" + filename)                                #获取文件夹路径
    for allDir in pathDir:
        # print allDir
        child = os.path.join(UPLOAD_FOLDER + "/" + '%s/%s' % (filename, allDir))        #获取统计文件夹内文件路径，并按coeff，raw，cal分类
        if 'coeff' in child:
            list_coeff.append(child)
        elif 'cal' in child:
            list_cal.append(child)
        else:
            list_raw.append(child)

    # print list_coeff
    # print list_cal
    # print list_raw

    fileDeal(filename, list_coeff, 'coeff')                                             #将文件路径列表分类传入fileDeal函数中处理
    # print list_coeff_ex
    fileDeal(filename, list_cal, 'cal')
    # print list_cal_ex
    fileDeal(filename, list_raw, 'raw')
    # print list_raw_ex

#---------------------文件读取函数--------------------------



#------------------------存储函数3--------------------------

def store_func(list1, list2, list3, filename, remark):                                  #类型三数据存储函数，存入informaldb数据库            
    client = InfluxDBClient('localhost', 8086, 'root', '', 'informaldb')                #数据分为coeff，raw，cal三个表存储
    # print list1[:10]
    for line in list1:
        time_coeff = line[0]
        bpf = line[2]
        bpf_diff = line[1]
        diff = line[3]

        json_body_coeff = [                                                             #参数coeff文件中数据的存储
            {
                "measurement": "coeff",
                "tags": {
                    "num": "3",
                    "filename": filename
                },
                "time": time_coeff,
                "fields": {
                    "coeff_bpf": bpf,
                    "coeff_bpf_diff": bpf_diff,
                    "coeff_diff": diff,
                    "remark": remark
                }
            }
        ]
        client.write_points(json_body_coeff)

    # print list2[:10]
    for line in list2:
        time_cal = line[0]
        res_cal_bd = float(line[1])
        he_cal = float(line[3])
        res_cal_bpf = float(line[6])
        res_cal_diff = float(line[5])
        total_cal = float(line[7])
        x_cal = float(line[8])
        y_cal = float(line[4])
        z_cal = float(line[2])

        json_body_cal = [                                                               #处理后数据文件cal中的数据存储
            {
                "measurement": "cal",
                "tags": {
                    "num": "3",
                    "res_cal_bd": res_cal_bd,
                    "he_cal": he_cal,
                    "res_cal_bpf": res_cal_bpf,
                    "res_cal_diff": res_cal_diff,
                    "total_cal": total_cal,
                    "filename": filename
                },
                "time": time_cal,
                "fields": {
                    "process": "1",
                    "x_cal": x_cal,
                    "y_cal": y_cal,
                    "z_cal": z_cal,
                    "remark": remark
                }
            }
        ]
        client.write_points(json_body_cal)

    # print list3[:10]
    for line in list3:
        time_raw = line[0]
        he_raw = float(line[1])
        total_raw = float(line[4])
        x_raw = float(line[5])
        y_raw = float(line[2])
        z_raw = float(line[3])

        json_body_raw = [                                                               #处理前数据文件raw中的数据存储
            {
                "measurement": "raw",
                "tags": {
                    "num": "3",
                    "he_raw": he_raw,
                    "total_raw": total_raw,
                    "filename": filename
                },
                "time": time_raw,
                "fields": {
                    "process": "0",
                    "x_raw": x_raw,
                    "y_raw": y_raw,
                    "z_raw": z_raw,
                    "remark": remark
                }
            }
        ]
        client.write_points(json_body_raw)

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')                   #存储类型三数据的同时存储相关信息到message数据库
    json_body = [
        {
            "measurement": "filename_filetype",
            "tags": {
                "filename": filename,
                "num": "3"
            },
            "fields": {
                "remark": remark
            }
        }
    ]
    client.write_points(json_body)

#------------------------存储函数3--------------------------



#-----------------------类sql语句查询功能--------------------

@app.route('/queryinput', methods=['GET', 'POST'])
def query_input():
    form = QueryForm()
    queryinput = None
    if form.validate_on_submit():
        queryinput = form.queryinput.data
        form.queryinput.data = ''
        database = form.database.data
        form.database.data = ''
        client = InfluxDBClient('localhost', 8086, 'root', '', database)
        result = client.query(queryinput)
        result_new = list(result.get_points())
        return render_template('lastquery.html', result=result_new)
    else:
        return render_template('queryinput.html', form=form)

#-----------------------类sql语句查询功能--------------------



#------------------------文件上传功能------------------------

@app.route('/uploadfile', methods=['GET', 'POST'])                                      #文件上传
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        choice = request.form["ps"]
        if file: #and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # print filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))              #将上传的文件存储在指定路径下            
            if choice == 'psa':                                                         #判断是否输入备注
                return redirect(url_for('upload_remark', filename=filename))            #返回备注输入页面
            else:
                remark = "Nothing"
                return redirect(url_for('uploaded_file', filename=filename, remark=remark))     #返回文件内容处理存储页面
    return render_template('upload.html')


@app.route('/uploadremark/<filename>', methods=['GET', 'POST'])                         #备注输入
def upload_remark(filename):
    form = RemarkForm()
    remark = None
    if form.validate_on_submit():
        remark = form.remark.data
        form.remark.data = ''
    if remark:
        return redirect(url_for('uploaded_file', filename=filename, remark=remark))
    else:
        return render_template('uploadremark.html', form=form)


@app.route('/uploads/<filename>/<remark>', methods=['GET', 'POST'])                     #文件内容处理及存储
def uploaded_file(filename, remark):
    if ('.txt' in filename) or ('.' not in filename):                                   #根据文件扩展名将文件分类处理(.txt文件和无扩展名文件)
        # print filename
        lines = []
        line_new = []
        line_fin = []
        f = open(UPLOAD_FOLDER + '/' + filename, "r")
        g = open(UPLOAD_FOLDER + '/' + filename, "r")
        lines = f.readlines()
        fencoding = chardet.detect(g.readline())
        code_type = fencoding['encoding']
        f.close()
        g.close()

        for line in lines:
            line = line[:-1]
            line = line.split(" ")
            line_new.append(line)
        dimension = len(line_new[0])

        if (8 <= dimension <= 12):                                                      #根据文件中数据属性的维数判断属于那种类型的数据
            i = 1
            for line in line_new:
                line_pix = line[0]
                line_pix = line_pix.decode(code_type)
                line[0] = line_pix[0:4] + '-' + \
                    line_pix[5:7] + '-' + line_pix[8:10]                                #将数据中的中文替换成标准格式
                line[0] = line[0].encode('gb2312')
                line_pro = line[0] + ' ' + line[1]
                # print line_pro
                filetime = datetime.datetime.strptime(line_pro, "%Y-%m-%d %H:%M:%S.%f")
                if i%2 == 0:
                    filetime = filetime + datetime.timedelta(seconds=0.1)
                finaltime = filetime.strftime("%Y-%m-%d %H:%M:%S.%f")
                list_final = finaltime.split(' ')

                line[0] = list_final[0]
                line[1] = list_final[1]
                # print line
                if '\r' in line[-1]:
                    line[-1] = line[-1][:-1]
                line_fin.append(line)
                i = i + 1
            # print line_fin

            store_func1(line_fin, filename, remark)
            os.system("rm uploadfiles/" + filename)                                     #文件数据存储完后，删除服务器中的源文件
        else:
            # print line_new
            form = DateForm()
            date = None
            if form.validate_on_submit():
                date = form.date.data
                form.date.data = ''
            if date:
                store_func2(line_new, filename, date, remark)
                os.system("rm uploadfiles/" + filename)
            else:
                return render_template('dateneed.html', form=form)
            
    elif '.rar' or '.zip' in filename:                                                  #压缩文件类型(.rar和.zip文件)
        filename_real = filename[:-4]
        os.system("mkdir uploadfiles/" + filename_real)
        os.system("unrar e uploadfiles/" + filename +
                  " uploadfiles/" + filename_real)

        global list_coeff, list_coeff_ex, list_cal, list_cal_ex, list_raw, list_raw_ex
        list_coeff = []
        list_coeff_ex = []
        list_cal = []
        list_cal_ex = []
        list_raw = []
        list_raw_ex = []

        eachFile(filename_real)
        store_func(list_coeff_ex, list_cal_ex, list_raw_ex, filename, remark)
        os.system("rm -r uploadfiles/" + filename_real)
        os.system("rm -r uploadfiles/" + filename)
        # print list_coeff
        # print list_coeff_ex

    else:                                                                               #其他可以扩展的格式，需要单独写新的处理及存储函数
        return filename

    return render_template('successful.html')
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#------------------------文件上传功能------------------------



#------------------------逐步查询功能-------------------------

@app.route('/querydata', methods=['GET', 'POST'])
def query_data():                                                                       #给出所有存储文件数据的数据库供选择
    client = InfluxDBClient('localhost', 8086, 'root', '', '')
    query = "show databases"
    result = client.query(query)
    result_new = list(result.get_points())
    return render_template('query.html', result=result_new)


@app.route('/queryresult', methods=['GET', 'POST'])                                     #根据选择的数据库给出所有表供选择
def query_result():
    database = request.form['database']
    client = InfluxDBClient('localhost', 8086, 'root', '', database)
    query = "show measurements"
    result = client.query(query)
    result_new = list(result.get_points())
    return render_template('query.html', result=result_new, name=database)


@app.route('/queryitems', methods=['GET', 'POST'])                                      #根据选择的表给出所有可供查询的属性项
def query_items():                                                                      #选择查询属性条件时必须至少包含一个field属性
    datament = request.form['datament']
    datament = datament.split('+')
    database = datament[0]
    measurement = datament[1]
    client = InfluxDBClient('localhost', 8086, 'root', '', database)
    query_tags = "show tag keys from" + " " + measurement
    query_fields = "show field keys from" + " " + measurement
    result_tags = client.query(query_tags)
    result_tags_list = list(result_tags.get_points())
    list_pop = []
    for item in result_tags_list:
        list_pop.append(item['tagKey'])

    result_fields = client.query(query_fields)
    result_fields_list = list(result_fields.get_points())
    list_bob = []
    for item in result_fields_list:
        list_bob.append(item['fieldKey'])

    return render_template('query.html', name=database, measurement=measurement, result_tags_list=list_pop, result_fields_list=list_bob)


@app.route('/lastquery', methods=['GET', 'POST'])                                       #根据查询条件给出最终查询结果
def last_query():
    tags = request.form.getlist("selected_tags")
    fields = request.form.getlist("selected_fields")
    database_measurement = request.form['database_measurement']
    database_measurement = database_measurement.split('+')
    database = database_measurement[0]
    measurement = database_measurement[1]
    print database
    print measurement
    # str_tags = ",".join(tags)
    # str_fields = ",".join(fields)
    query_tags = "select "
    for tag in tags:
        query_tags = query_tags + tag + ","
    for field in fields:
        query_tags = query_tags + field + ","
    query_tags = query_tags[:-1] + " from " + measurement
    client = InfluxDBClient('localhost', 8086, 'root', '', database)
    result = client.query(query_tags)
    result_new = list(result.get_points())

    return render_template('lastquery.html', result=result_new)

#------------------------逐步查询功能-------------------------



#-----------------------数据删除功能-----------------------

@app.route('/dropmeasurement', methods=['GET', 'POST'])                                 #给出操作选择项，删除表还是根据文件名删除相关数据流
def measurement_drop():
    if request.method == 'POST':
        choice = request.form['choice']
        
        if choice == "dm":                                                              #选择删除表
            client = InfluxDBClient('localhost', 8086, 'root', '', '')
            query = "show databases"
            result = client.query(query)
            result_new = list(result.get_points())
            list_all = []
            for item in result_new:
                db = item['name']
                list_mea = [db]
                client = InfluxDBClient('localhost', 8086, 'root', '', db)
                query = "show measurements"
                result_mea = client.query(query)
                result_mea_new = list(result_mea.get_points())
                for temp in result_mea_new:
                    list_mea.append(temp['name'])
                list_all.append(list_mea)
            return render_template('dropdata.html', list_all=list_all[1:])

        else:                                                                           #选择删除数据流
            client = InfluxDBClient('localhost', 8086, 'root', '', 'message')
            query = "select * from filename_filetype"
            result = client.query(query)
            result_new = list(result.get_points())
            list_filename = []
            for item in result_new:
                list_temp = []
                list_temp = [item['filename'], item['num'], item['remark']]
                if list_temp not in list_filename:
                    list_filename.append(list_temp)

            return render_template('dropdata.html', result=list_filename)
    return render_template('dropdata.html')

@app.route('/dropdeal', methods=['GET', 'POST'])                                        #处理数据表的删除
def drop_deal():
    list_message = []
    list_meas = request.form.getlist("selected_meas")
    database = request.form['database']
    client = InfluxDBClient('localhost', 8086, 'root', '', database)
    for mea in list_meas:
        query = "drop measurement " + mea
        client.query(query)
        if mea == "data_type_1":
            if "1" not in list_message:
                list_message.append("1")
        elif mea == "data_type_2":
            if "2" not in list_message:
                list_message.append("2")
        else:
            if "3" not in list_message:
                list_message.append("3")

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')                   #在message数据库中也要删除相关信息
    for temp in list_message:
        query = "drop series where num = '%s'" % temp
        client.query(query)

    return render_template('dropdata.html')

@app.route('/dropfile', methods=['GET', 'POST'])                                        #处理数据流的删除
def drop_file():
    filename_num = request.form['filename']
    list_filenum = filename_num.split('+')
    num = list_filenum[1]
    filename = list_filenum[0]
    if num == '3':
        client = InfluxDBClient('localhost', 8086, 'root', '', 'informaldb')
        query_raw = "drop series from raw where filename = '%s'" % filename
        query_cal = "drop series from cal where filename = '%s'" % filename
        query_coeff = "drop series from coeff where filename = '%s'" % filename
        client.query(query_raw)
        client.query(query_cal)
        client.query(query_coeff)
    else:
        client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')
        if num == '1':
            query = "drop series from data_type_1 where filename = '%s'" % filename
            client.query(query)
        else:
            query = "drop series from data_type_2 where filename = '%s'" % filename
            client.query(query)

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')                   #在message数据库中删除相关信息
    query_drop = "drop series from filename_filetype where filename = '%s'" % filename
    client.query(query_drop)

    return render_template('dropdata.html')

#-----------------------数据表删除功能-----------------------



@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
