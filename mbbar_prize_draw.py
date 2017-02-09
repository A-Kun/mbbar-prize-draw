#!usr/bin/env python
# -*- coding: utf8 -*-


"""
# Copyright Andrew Wang, 2017
# Distributed under the terms of the GNU General Public License.
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
"""


from io import open
from os.path import expanduser
from Tkinter import *
import tkMessageBox
import csv
import os
import random


HOME = expanduser("~")
OUTPUT = HOME + '/Desktop/result.csv'
PAGE_COUNT = [1]
SOFTWARE = {u'1Password': 2,
            u'CleanMyMac': 2,
            u'CmdTap': 3,
            u'Disk Drill': 1,
            u'Jitouch': 1,
            u'KeyCue': 3,
            u'PDF Expert': 2,
            u'TotalFinder': 1,
            u'Volume Mixer': 1}
EXCLUDE = {u'假的MJ狂Fan'}
result = {}


def read_thread_users(content):
    ID_IDENTIFIER = """fr=pb&ie=utf-8" target="_blank">"""
    ID_CLOSE_TAG = """</a>"""
    LV_IDENTIFIER = """level_id&quot;:"""
    TEXT_IDENTIFIER = """class="d_post_content j_d_post_content  clearfix">"""
    TEXT_CLOSE_TAG = """</div>"""
    COMMA = ""","""

    content1 = content
    content2 = content
    content3 = content

    lvs = []
    index = content1.find(LV_IDENTIFIER)
    while index != -1:
        index_start = index + len(LV_IDENTIFIER)
        index_end = content1.find(COMMA, index_start)
        next_id = content1[index_start:index_end]
        lvs.append(next_id)
        content1 = content1[index_end + len(COMMA):]
        index = content1.find(LV_IDENTIFIER)

    ids = []
    index = content2.find(ID_IDENTIFIER)
    while index != -1:
        index_start = index + len(ID_IDENTIFIER)
        index_end = content2.find(ID_CLOSE_TAG, index_start)
        next_id = content2[index_start:index_end]
        ids.append(next_id)
        content2 = content2[index_end + len(ID_CLOSE_TAG):]
        index = content2.find(ID_IDENTIFIER)

    texts = []
    index = content3.find(TEXT_IDENTIFIER)
    while index != -1:
        index_start = index + len(TEXT_IDENTIFIER)
        index_end = content3.find(TEXT_CLOSE_TAG, index_start)
        next_text = content3[index_start:index_end]
        texts.append(next_text)
        content3 = content3[index_end + len(TEXT_CLOSE_TAG):]
        index = content3.find(TEXT_IDENTIFIER)

    default_soft = {}
    for next_soft in SOFTWARE:
        default_soft[next_soft] = 0
    default_soft.update({'hardware_bonus': 0, 'software_bonus': 0})

    for i in range(len(lvs)):
        if ids[i] in result:
            if result[ids[i]]['post_bonus'] < 3:
                result[ids[i]]['post_bonus'] += 1
            result[ids[i]]['text'] += texts[i].lower().replace(' ', '').replace('-', '')
        else:
            if int(lvs[i]) >= 9:
                lv_bonus = (int(lvs[i]) - 8) * 2
            else:
                lv_bonus = 0
            result[ids[i]] = {'lv': int(lvs[i]), 'lv_bonus': lv_bonus, 'post_bonus': 1, 'text': texts[i].lower().replace(' ', '').replace('-', '')}
            result[ids[i]].update(default_soft)

    for next_id in result:
        for next_soft in SOFTWARE:
            if next_soft.lower().replace(' ', '').replace('-', '') in result[next_id]['text']:
                result[next_id][next_soft] = 10
                result[next_id]['software_bonus'] = 10
        if u'软件' in result[next_id]['text'] or u'app' in result[next_id]['text']:
            result[next_id]['software_bonus'] = 10
        if u'13inch' in result[next_id]['text'] or u'13寸' in result[next_id]['text'] or u'十三寸' in result[next_id]['text']:
            result[next_id]['hardware_bonus'] = 10

    PAGE_COUNT[0] += 1
    prompt1.configure(text='提取成功')
    prompt2.configure(text='请粘贴帖子第' + str(PAGE_COUNT) + '页的源代码：')
    T1.delete('1.0', END)


def read_from_ui():
    T1_text = T1.get('1.0', END)
    read_thread_users(T1_text)


def write_to_file():
    if tkMessageBox.askyesno("", "点击确定后将弹出统计结果并开始抽奖。"):
        for next_ex in EXCLUDE:
            if next_ex in result:
                del result[next_ex]

        soft_list_encoded = list(SOFTWARE.keys())
        for i in range(len(soft_list_encoded)):
            soft_list_encoded[i] = soft_list_encoded[i].encode('utf-8')

        with open(OUTPUT, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            titles = ['id', 'lv', 'lv_bonus', 'post_bonus'] + list(SOFTWARE.keys()) + ['text']
            write_titles = ['id', 'lv', 'lv_bonus', 'post_bonus', 'hardware_bonus', 'software_bonus'] + soft_list_encoded + ['text']
            writer.writerow(write_titles)
            for next_id in result:
                next_row = [next_id, result[next_id]['lv'], result[next_id]['lv_bonus'], result[next_id]['post_bonus'], result[next_id]['hardware_bonus'], result[next_id]['software_bonus']]
                for next_soft in SOFTWARE:
                    next_row.append(result[next_id][next_soft])
                for i in range(len(next_row)):
                    if type(next_row[i]) is unicode:
                        next_row[i] = next_row[i].encode('utf-8')
                    else:
                        next_row[i] = str(next_row[i])
                next_row.append(result[next_id]['text'].encode('utf-8'))
                writer.writerow(next_row)
        os.system('open -a Numbers.app ' + OUTPUT)

        draw()

        tkMessageBox.showinfo("", "抽奖结果已输出至终端。")


def draw():
    for i in range(6):
        draw_list = []
        for next_id in result:
            bonus = result[next_id]['lv_bonus'] + result[next_id]['post_bonus'] + result[next_id]['hardware_bonus']
            for j in range(bonus):
                draw_list.append(next_id)
        random.shuffle(draw_list)
        print 'Tomtoc 电脑包:',
        print draw_list[0],
        print '(' + str(draw_list.count(draw_list[0])) + 'x)'
        del result[draw_list[0]]

    items = SOFTWARE.keys()
    for next_item in items:
        for i in range(SOFTWARE[next_item]):
            draw_list = []
            for next_id in result:
                bonus = result[next_id]['lv_bonus'] + result[next_id]['post_bonus'] + result[next_id]['software_bonus'] + result[next_id][next_item]
                for j in range(bonus):
                    draw_list.append(next_id)
            random.shuffle(draw_list)
            print next_item + ':',
            print draw_list[0],
            print '(' + str(draw_list.count(draw_list[0])) + 'x)'
            del result[draw_list[0]]


if __name__ == '__main__':
    root = Tk()
    root.title('')

    info1 = Label(root, text="MacBook吧新年活动抽奖器", fg='red')
    info1.pack()

    info2 = Label(root, text="by @a1223364 / @A君君君君", fg='red')
    info2.pack()

    gap = Label(root, text="")
    gap.pack()

    prompt1 = Label(root, text="", fg="darkgreen")
    prompt1.pack()

    prompt2 = Label(root, text='请粘贴帖子第' + str(PAGE_COUNT) + '页的源代码：')
    prompt2.pack()

    T1 = Text(root, height=4, width=50)
    T1.pack()

    btn1 = Button(root, text="开始导入", command=read_from_ui)
    btn1.pack()

    btn2 = Button(root, text="完成导入", command=write_to_file)
    btn2.pack()

    mainloop()
