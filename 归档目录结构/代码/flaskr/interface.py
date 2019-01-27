# -*- coding: utf-8 -*-

import os
from influxdb import InfluxDBClient


#--------------------------获取数据库中存储的所有文件名---------------------------

def getalldatafilename():
    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')
    query = "select * from filename_filetype"
    result = client.query(query)
    result_new = list(result.get_points())
    list_file = []
    for item in result_new:
        list_temp = []
        list_temp = [item['filename'], item['num'], item['remark']]
        if list_temp not in list_file:
            list_file.append(list_temp)

    if list_file:
        return list_file
    else:
        return False

#--------------------------获取数据库中存储的所有文件名---------------------------



#----------------------根据文件名获取所有数据（返回数据有固定格式）--------------------

def getdatabyname(filename, datatype, chs):
    if datatype == '1':
        result_final = [['1']]
        client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')
        query = "select * from data_type_1 where filename = '%s'" % filename
        # print query
        result = client.query(query)
        result_new = list(result.get_points())
        for item in result_new:
            result_app = [item['time'],item['latitude'], item['longitude'], item['height'], item['x_axis_component'], item['y_axis_component'], item['z_axis_component'], item['channel_1_total_field'], item['channel_2_total_field']]
            result_final.append(result_app)
        return result_final

    elif datatype == '2':
        result_final = []
        client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')
        query = "select * from data_type_2 where filename = '%s'" % filename
        result = client.query(query)
        result_new = list(result.get_points())
        for item in result_new:
            result_app = [item['x_axis_component'], item['y_axis_component'], item['z_axis_component'], [item['Mag_1_raw_TF'], item['Mag_2_raw_TF'], item['Mag_3_raw_TF'], item['Mag_4_raw_TF']], [item['fourth_Diff_Mag_1_raw_TF'], item['fourth_Diff_Mag_2_raw_TF'], item['fourth_Diff_Mag_3_raw_TF'], item['fourth_Diff_Mag_4_raw_TF']], [item['Mag_1_TF_uncomp'], item['Mag_2_TF_uncomp'], item['Mag_3_TF_uncomp'], item['Mag_4_TF_uncomp']], [item['Mag_1_TF_comp'], item['Mag_2_TF_comp'], item['Mag_3_TF_comp'], item['Mag_4_TF_comp']], [item['Grad_1_uncomp'], item['Grad_2_uncomp'], item['Grad_3_uncomp']], [item['Grad_1_comp'], item['Grad_2_comp'], item['Grad_3_comp']], item['time']]
            result_final.append(result_app)
        if item['Mag_3_raw_TF'] and item['Mag_4_raw_TF']:
            sum = 4
        elif item['Mag_3_raw_TF']:
            sum = 3
        else:
            sum = 2
        op = [['2', sum]]
        result_final = op + result_final
        return result_final

    else:
        result_final = []
        client = InfluxDBClient('localhost', 8086, 'root', '', 'informaldb')
        if chs == '0':
            query = "select * from raw where filename = '%s'" % filename
            result_raw = client.query(query)
            result_raw_new = list(result_raw.get_points())
            for item in result_raw_new:
                result_raw_app = [item['x_raw'], item['y_raw'], item['z_raw'], item['total_raw'], item['he_raw'], None, None, None, item['time']]
                result_final.append(result_raw_app)
            op = [['3', '0', None, None, None]]
            result_final = op + result_final
            return result_final
        else:
            result_final = []
            query_cal = "select * from cal where filename = '%s'" % filename
            # query_coeff = "select * from coeff where filename = '%s'" % filename
            result_cal = client.query(query_cal)
            # result_coeff = client.qeury(query_coeff)
            result_cal_new = list(result_cal.get_points())
            # result_coeff_new = list(result_coeff.get_points())
            for item in result_cal_new:
                result_cal_app = [item['x_cal'], item['y_cal'], item['z_cal'], item['total_cal'], item['he_cal'], item['res_cal_bd'], item['res_cal_bpf'], item['res_cal_diff'], item['time']]
                result_final.append(result_cal_app)
            # for coeff in result_coeff_new:
            #   result_coeff_app = [item]
            op = [['3', '1', None, None, None]]
            result_final = op + result_final
            return result_final

#----------------------根据文件名获取所有数据（返回数据有固定格式）--------------------



#---------------------------类型一数据存储函数---------------------------------

def store_func1(lines, filename):
    client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')
    query = "drop series from data_type_1 where filename = '%s'" % filename
    client.query(query)
    for line in lines:
        time_x1 = line[0]
        latitude_x1 = line[1]
        longitude_x1 = line[2]
        height_x1 = line[3]
        component_x1 = float(line[4])
        component_y1 = float(line[5])
        component_z1 = float(line[6])
        field_channel1 = line[7]
        field_channel2 = line[8]
        remark = "Nothing"

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

        
        client.write_points(json_body_1)

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')
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

#---------------------------类型一数据存储函数---------------------------------



#---------------------------类型二数据存储函数--------------------------------

def store_func2(lines, filename, summer, data_add):
    client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')
    query = "drop series from data_type_2 where filename = '%s'" % filename
    client.query(query)
    dimension = len(lines)
    for i in range(0, dimension):
        # dimension = len(line)
        scan_number = data_add[i][0]
        input_tags = data_add[i][1]
        component_x2 = float(lines[i][0])
        component_y2 = float(lines[i][1])
        component_z2 = float(lines[i][2])
        remark = "Nothing"

        if summer == 4:
            raw_mag1 = lines[i][3][0]
            raw_mag2 = lines[i][3][1]
            raw_mag3 = lines[i][3][2]
            raw_mag4 = lines[i][3][3]

            diff_mag1 = lines[i][4][0]
            diff_mag2 = lines[i][4][1]
            diff_mag3 = lines[i][4][2]
            diff_mag4 = lines[i][4][3]

            uncomp_mag1 = lines[i][5][0]
            uncomp_mag2 = lines[i][5][1]
            uncomp_mag3 = lines[i][5][2]
            uncomp_mag4 = lines[i][5][3]

            comp_mag1 = lines[i][6][0]
            comp_mag2 = lines[i][6][1]
            comp_mag3 = lines[i][6][2]
            comp_mag4 = lines[i][6][3]

            uncomp_grad1 = lines[i][7][0]
            uncomp_grad2 = lines[i][7][1]
            uncomp_grad3 = lines[i][7][2]

            comp_grad1 = lines[i][8][0]
            comp_grad2 = lines[i][8][1]
            comp_grad3 = lines[i][8][2]

            time_y2 = lines[i][9]  # 时间待修改，加上文件名日期

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

        elif summer == 3:
            raw_mag1 = lines[i][3][0]
            raw_mag2 = lines[i][3][1]
            raw_mag3 = lines[i][3][2]

            diff_mag1 = lines[i][4][0]
            diff_mag2 = lines[i][4][1]
            diff_mag3 = lines[i][4][2]

            uncomp_mag1 = lines[i][5][0]
            uncomp_mag2 = lines[i][5][1]
            uncomp_mag3 = lines[i][5][2]

            comp_mag1 = lines[i][6][0]
            comp_mag2 = lines[i][6][1]
            comp_mag3 = lines[i][6][2]

            uncomp_grad1 = lines[i][7][0]
            uncomp_grad2 = lines[i][7][1]

            comp_grad1 = lines[i][8][0]
            comp_grad2 = lines[i][8][1]

            time_y2 = lines[i][9]

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

        else:
            raw_mag1 = lines[i][3][0]
            raw_mag2 = lines[i][3][1]

            diff_mag1 = lines[i][4][0]
            diff_mag2 = lines[i][4][1]

            uncomp_mag1 = lines[i][5][0]
            uncomp_mag2 = lines[i][5][1]

            comp_mag1 = lines[i][6][0]
            comp_mag2 = lines[i][6][1]

            uncomp_grad1 = lines[i][7][0]

            comp_grad1 = lines[i][8][0]

            time_y2 = lines[i][9]

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

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')
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

#---------------------------类型二数据存储函数------------------------------



#---------------------------类型三数据存储函数------------------------------

def store_func3(lines, process, filename):
    client = InfluxDBClient('localhost', 8086, 'root', '', 'informaldb')
    if process == '0':
        query = "drop series from raw where filename = '%s'" % filename
        client.query(query)
        for line in lines:
            x_raw = line[0]
            y_raw = line[1]
            z_raw = line[2]
            total_raw = line[3]
            he_raw = line[4]
            time_raw = line[8]
            remark = "Nothing"

            json_body_raw = [
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

    else:
        query = "drop series from cal where filename = '%s'" % filename
        client.query(query)
        for line in lines:
            x_cal = line[0]
            y_cal = line[1]
            z_cal = line[2]
            total_cal = line[3]
            he_cal = line[4]
            res_cal_bd = line[5]
            res_cal_bpf = line[6]
            res_cal_diff = line[7]
            time_cal = line[8]
            remark = "Nothing"
            json_body_cal = [
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

    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')
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

#---------------------------类型三数据存储函数------------------------------



#--------------------------将返回的经过滤波处理的数据存入数据库--------------------------

def writedata(filename, datatype, data):
    if datatype == '1':
        data_real = data[1:]
        filename  = filename + '_pro'
        store_func1(data_real, filename)

    elif datatype == '2':
        result_final = []
        data_real = data[1:]
        summer = data[0][1]
        client = InfluxDBClient('localhost', 8086, 'root', '', 'formaldb')
        query = "select Fiducial_number,Event_input_tags,remark from data_type_2 where filename = '%s'" % filename
        result = client.query(query)
        result_new = list(result.get_points())
        for item in result_new:
            result_app = [item['Fiducial_number'], item['Event_input_tags']]
            result_final.append(result_app)
        # return result_final
        filename = filename + '_pro'
        store_func2(data_real, filename, summer, result_final)

    else:
        data_real = data[1:]
        filename = filename + '_pro'
        process = data[0][1]
        store_func3(data_real, process, filename)

#--------------------------将返回的经过滤波处理的数据存入数据库--------------------------



#--------------------------根据文件名获取文件属性-------------------------

def getattrbyfilename(filename):
    client = InfluxDBClient('localhost', 8086, 'root', '', 'message')
    query = "select num,remark from filename_filetype where filename = '%s'" % filename
    result = client.query(query)
    result_new = list(result.get_points())
    result_app = result_new[0]
    result_type = result_app['num']
    result_ps = result_app['remark']
    if result_type == '1':
        return ['1', result_ps]
    elif result_type == '2':
        return ['2', result_ps]
    else:
        return ['3', None, None, None, None, result_ps]

#--------------------------根据文件名获取文件属性-------------------------



print getalldatafilename()
print getattrbyfilename("05-20-201611-54-35.rar")