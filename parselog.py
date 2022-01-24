# coding=utf-8

"""
com.apple.xpc.launchd[1] (com.apple.mdworker.bundles[12555])

设备名称: (deviceName)    BBAOMACBOOKAIR2
错误的进程号码: (processId) 158
进程/服务名称: (processName)  timed[158]
错误的原因（描述）(description)
发生的时间（小时级），例如 0100-0200，0300-0400, (timeWindow)     May 13 00:02:12
在小时级别内发生的次数 (numberOfOccurrence)    统计

1 多行匹配
2 时间转化
3 正则表达式
4 last message repeated 1 time
5 重复行定义 ?
6 线程or进程
7 生成的格式
[
    {
        "deviceName": "BBAOMACBOOKAIR2",
        "hash": "2c51f2574b0bb56eba366c7a4cb4c859",
        "description": "Entered:__thr_AMMuxedDeviceDisconnected,",
        "processId": "976",
        "timeWindow": "1400-1500",
        "processName": "AMPDeviceDiscoveryAgent",
        "numberOfOccurrence": 1
    },
    {
        "deviceName": "BBAOMACBOOKAIR2",
        "hash": "6df9c153eaff4266e05610a07371b886",
        "description": "tid:8777 - Mux ID not found in mapping",
        "processId": "976",
        "timeWindow": "1400-1500",
        "processName": "AMPDeviceDiscoveryAgent",
        "numberOfOccurrence": 13
    },
    {
        "deviceName": "BBAOMACBOOKAIR2",
        "hash": "d48a31479be3932c961225a9a929e6e5",
        "description": "tid:8777 - Can't handle disconnect with invalid",
        "processId": "976",
        "timeWindow": "1400-1500",
        "processName": "AMPDeviceDiscoveryAgent",
        "numberOfOccurrence": 13
    },
]

上传格式
json upload to https://foo.com/bar
[
    {
        "hash": "",
        "deviceName": "",
        "processId": "",
        "processName": "",
        "description": "",
        "timeWindow": "0100-0200",
        "numberOfOccurrence": ""
    }
]

"""

import re
import hashlib
import json
import gzip
import requests


def translate_time(hour):
    if hour.startswith('0'):
        start_time = hour + '00'
        end_time = str(int(hour) + 1) + '00'
    elif int(hour) == 23:
        start_time = '2300'
        end_time = '0000'
    else:
        start_time = hour + '00'
        end_time = str(int(hour) + 1) + '00'
    return "%s-%s" % (start_time, end_time)


def split_process_id(processid):
    # 1 com.apple.xpc.launchd[1] (com.apple.mdworker.bundles[12560]):
    # 2 timed[158]:
    re_process = re.compile(r'(.*)\[(\d+)\]:?')
    res = re_process.findall(processid)
    if res:
        return res[0]
    else:
        return ("-", "-")


def gen_hash(line):
    md = hashlib.md5()
    md.update(line.encode('utf-8'))
    return md.hexdigest()


def date_match(line):
    return bool(re.match(r'^\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}\s', line))


def yeild_matches(full_log):
    log = []
    for line in full_log.split("\n"):
        # print(line)
        if date_match(line):
            if len(log) > 0:
                yield "\t".join(log)
                log = []
        log.append(line)
    yield "\n".join(log)


def main():
    res = []
    check_dict = {}
    new_logs = []
    with gzip.open('./DevOps_interview_data_set.gz', 'r') as f:
        data = f.read()
    # 将多行合并为单行
    logs = list(yeild_matches(data))
    # 将重复的行替换
    for inx, line in enumerate(logs):
        repeat_line = re.compile(r'.* --- last message repeated (\d+) time ---')
        repeat_nums = repeat_line.findall(line)

        if not repeat_nums:
            new_logs.append(line)
        else:
            for _ in range(int(repeat_nums[0])):
                if inx > 0:
                    # print("repeat line to new_log " + logs[inx - 1])
                    new_logs.append(logs[inx - 1])

    # 此时new_logs 为清理后的数据
    for idx, line in enumerate(new_logs):
        # 对于行的处理
        origin_list = line.split()
        # 数据解析
        timeWindow = translate_time(origin_list[2].split(":")[0])
        (processName, processId) = split_process_id(origin_list[4])
        deviceName = origin_list[3]
        description = " ".join(origin_list[5:-1])

        # 以前三个字段进行hash
        line_hash = gen_hash("".join(origin_list[3:]))
        if line_hash not in check_dict:
            # 如果不存在
            # check_dict[line_hash] = {}
            # check_dict[line_hash]["number"] = 1
            # check_dict[line_hash]["index"] = idx  #newlog index
            check_dict[line_hash] = 1

            resdict = {
                "hash": line_hash,
                "deviceName": deviceName,
                "processName": processName,
                "processId": processId,
                "description": description,
                "timeWindow": timeWindow,
                "numberOfOccurrence": 1
            }
            res.append(resdict)
        else:
            # print(res)
            check_dict[line_hash] += 1
            # print(res[check_dict[line_hash]['index']])
            # 已经存在,直接更新numberOfOccurrence
            for index, li in enumerate(res):
                if li['hash'] == line_hash:
                    res[index]['numberOfOccurrence'] += 1

            # res[check_dict[line_hash]['index']]["numberOfOccurrence"] += 1

    json_res = json.dumps(res, indent=4)
    print(json_res)

    post_url = "https://foo.com/bar"
    x = requests.post(post_url, data=json_res)
    print(x.text)


if __name__ == '__main__':
    main()
