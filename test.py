import copy
import csv
import datetime
import json
import os
import re
import shutil
import subprocess
import time
import webbrowser

import pyautogui
import pyperclip

import chardet
import pysrt
from PyQt5 import Qt, QtCore, QtGui
from PyQt5.QtCore import QRectF, QRect, QSizeF, QTimer, QSettings, pyqtSignal, QEvent
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QFont, QTextOption, QTextDocument, QTextCursor, QTextCharFormat, \
    QKeySequence, QPixmap, QIcon, QPalette, QTextBlockFormat
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QGraphicsScene, QPushButton, QHBoxLayout, \
    QWidget, QVBoxLayout, QSizePolicy, QSlider, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem, \
    QGraphicsDropShadowEffect, QMenu, QDialog, QDockWidget, QListWidget, QLabel, QLineEdit, QTextEdit, QShortcut, \
    QInputDialog, QDialogButtonBox, QSpinBox, QActionGroup
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from bs4 import BeautifulSoup
from moviepy.video.io.VideoFileClip import VideoFileClip
from readmdict import MDX
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common import credential
from tencentcloud.tmt.v20180321 import models
from tencentcloud.tmt.v20180321 import tmt_client
import concurrent.futures

print("开始加载词典")
filename = "韦氏高阶英汉双解词典v3.mdx"
headwords = [*MDX(filename)]  # 单词目录，对象为数组,元素为字节
items = [*MDX(filename).items()]  # 单词和释义
print("词典加载完毕")
cssfile = '''
<!DOCTYPE html>
<html>
<head>
<script>
document.addEventListener("DOMContentLoaded", function() {
  var radios = document.querySelectorAll('input[type="radio"][name="options"]');

  radios.forEach(function(radio) {
    radio.addEventListener("change", function() {
      if (this.checked) {
        var labelText = this.parentNode.innerHTML;
        console.log(labelText);
      }
    });
  });
});
</script>
<style>
body {margin:0; padding: 0; word-wrap: break-word!important; font-family: "Helvetica Neue",Helvetica, Arial,"PingFang SC","Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;line-height:1.2em;}

div.text_prons, span.hpron_word, div.fl {display:inline;padding-right:5px;}
div.d_hidden {display:none}
/*ul {margin:0;padding:0;}*/
/*li {margin:0 0 0 15px;padding:0 0 0 5px;}*/
div.hw_infs_d, div.labels, span.gram {display:inline;}

#ld_entries_v2_mainh{font-size:180%;font-weight:bold;color:#003399;}
#ld_entries_v2_others_block{margin-top:5px;}
#ld_entries_v2_others_block > .o_count{color:#777777;margin-bottom:4px;margin-top:0px;font-variant: small-caps;}
#ld_entries_v2_others_block > .o_list{}
#ld_entries_v2_others_block > .o_list{border:1px solid #ccc;list-style-type: none;padding:0px;margin:0px;height: 72px;overflow: hidden;overflow-y: auto;}
#ld_entries_v2_others_block > .o_list > li{margin:0;padding:0;}
#ld_entries_v2_others_block > .o_list > li > a{padding: 4px 3px 4px 15px;text-decoration: none;display:block;font-weight:bold;}
#ld_entries_v2_others_block > .o_list > li > a.selected:first-child{background-color:#E8F5F6;color:#000;}
#ld_entries_v2_others_block > .o_list > li > a:hover{background-color:#F0F0F0;color:black;}
#ld_entries_v2_others_block > .o_list > li > a > span{font-weight:normal !important;}
#ld_entries_v2_all{padding:10px;border:1px solid #ccc;border-radius:10px;margin:auto;position:relative;}

/*delete save part for GD*/
#ld_entries_v2_all > .save_faves > .txt{display:none;}

/*utils*/
.entry_v2 .vfont{display:none;} /*for GD*/

/*mw markup overrides*/
.entry_v2 .mw_spm_aq{color:#000;margin:0;padding:0;padding:0;border:none;}

/*Dotted line*/
.entry_v2 .dline {display:none;}

/*non-HW prons*/
.entry_v2 .pron_l_b{}
.entry_v2 .pron_l_a{}
.entry_v2 .pron_w{color:#717274;font-weight:normal;font-size:109%;}
.uro_line .pron_w{color:#717274;font-weight:normal;font-size:109%;}
.entry_v2 .pron_i{color:#D40218;}
.entry_v2 .pron_i:hover{color:#FF0000;text-decoration: none;}

/*non-HW variations*/
.entry_v2 .v_label{font-style: italic;color:#009900;}
.entry_v2 .v_text{font-weight:bold;}

/*non-HW inflections*/
.entry_v2 .i_label{font-style:italic;color:#757575;}
.entry_v2 .i_text{font-weight:bold; color:#0B5BC4;}
.uro_line > .i_label{font-weight:bold; color:#757575;}
.uro_line > .i_text{font-weight:bold; color:#0B5BC4;}

/*single word entry resets*/
.entry_v2 p {margin:0;padding:0 0 10px 0;font-weight:normal;}
.entry_v2 a{color:#1122CC;text-decoration:none;}
.entry_v2 a:hover{text-decoration:underline;}
.sms a{color:#1122CC;text-decoration:none; font-size: 110%; }
.sms a:hover{text-decoration:underline;}
.sms {color: #808080; font-size: 90%;}
.entry_v2 > .goto_main::before {content: "⇒ Main Entry: "; color:#808080; display: inline; font-size: 90%;} 

/*desktop: headword*/
.entry_v2 > .hw_d{font-size: 95%;margin: 0px -10px 1em -10px;background-color: #E7F5F5;padding: 0 50px 0 20px;position: relative;}
.entry_v2 > .hw_d.hw_0{border-top-left-radius:10px;border-top-right-radius:10px;margin:-10px -10px 1em -10px;}
.entry_v2 > .hw_d.hw_0.hw_wod{margin:0;background-color:transparent;padding:10px 0px;}
.entry_v2 > .hw_d > * {position:relative;vertical-align:middle;}
.entry_v2 > .hw_d > .hw_txt{font-size:150%; font-weight: bold; color:#032952; line-height: 1.5em;}
.entry_v2 > .hw_d > .hw_txt > sup{margin-right:2px;}
.entry_v2 > .hw_d > .hsl{margin-left:6px;font-style:italic;}
.entry_v2 > .hw_d > .hpron_label_a{margin-left:7px;}
.entry_v2 > .hw_d > .hpron_label_b{margin-left:7px;}
.entry_v2 > .hw_d > .hpron_word{color:#525157;font-weight:normal;margin-left:17px;font-size:109%;}
.entry_v2 > .hw_d > .hpron_icon{color:#D40218;font-size:110%;margin-left:7px;}
.entry_v2 > .hw_d > .hpron_icon:hover{text-decoration: none;}
.entry_v2 > .hw_d > .fl{color:#8f0610;font-style:italic;font-weight: bold;margin-left:8px;}
.uro_line > .fl{color:#8f0610;font-style:italic;font-weight: bold;margin-left:8px;}
.dro_line > .dre{font-size:145%; font-weight: bold; color:#032952;}
.uro > .uro_line > .ure{font-size:145%; font-weight: bold; color:#032952;}

/*desktop: headword variations*/
.entry_v2 > .hw_vars_d{margin-bottom:.6em;}

/*desktop: headword inflections*/
.entry_v2 > .hw_infs_d{margin-bottom:.6em;}


/*view: entry level labels*/
.entry_v2 > .labels{margin:0;}
.entry_v2 > .labels > .lb{font-style:italic;}
.entry_v2 > .labels > .gram{}
.entry_v2 > .labels > .gram > .gram_internal{color:#009900;}
.gram > .gram_internal{color:#009900;}
.entry_v2 > .labels > .sl{font-style:italic;}

/*view: phrasal verbs*/
.entry_v2 .pvl{}
.entry_v2 .pva{font-weight:bold;}

/*view: synonym paragraphs*/
.entry_v2 .synpar{border:1px solid #ccc;padding:4px 10px 6px 10px;margin-bottom:4em;}
.entry_v2 .synpar > .synpar_part{margin-bottom:5px;}
.entry_v2 .synpar > .synpar_part:last-child{margin-bottom:0;}
.entry_v2 .synpar > .synpar_part > .synpar_w{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .synpar > .synpar_part > .syn_par_t{}
.entry_v2 .synpar > .synpar_part > *:last-child{margin-bottom:0;}

/*view: supplementary notes*/
.entry_v2 .snotes{margin-bottom:.5em;overflow:hidden;}
.entry_v2 .snotes > *{margin-bottom:0.4em;}
.entry_v2 .snotes > *:last-child{margin-bottom:0;}
.entry_v2 .snotes > .snote_text{}
.entry_v2 .snotes > .snote_text > .snote_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .snotes > .snote_text > .snote_link sup{font-size:50%;}

/*view: supplementary noteboxes*/
.entry_v2 .snotebox{border:1px solid #ccc;padding:0.8em;margin-bottom:.5em;overflow:hidden;}
.entry_v2 .snotebox > .snotebox_text{text-align:justify;}
.entry_v2 .snotebox > .snotebox_text > .snote_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .snotebox > .snotebox_text > .snote_link sup{font-size:50%;}

/*view: art*/
.entry_v2 .arts{margin-bottom:.5em;}
.entry_v2 .arts > .art{text-align: center;margin-bottom:4px;}
.entry_v2 .arts > .art:last-child{margin-bottom:0;}
.entry_v2 .arts > .art > img{border:1px solid #ddd;padding-top:0px;max-width:100%;}

/*view: usage note*/
.entry_v2 .un_text{}

/*view: sense blocks*/
.entry_v2 .sblocks{margin-bottom:.5em;}
.entry_v2 .sblocks > .sblock{width:100%;margin:0px 0px 0px 0px;}
.entry_v2 .sblocks > .sblock > .sblock_c{margin-bottom:4px;}
.entry_v2 .sblocks > .sblock > .sblock_c:last-child{margin-bottom:0;}
.entry_v2 .sblocks > .sblock > .sblock_c > .sn_block_num{float:left;font-weight:bold;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels{}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .slb{font-style:italic; color:#757575;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .ssla{font-style:italic; color: #009900;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .sgram{}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .sgram > .sgram_internal{color:#009900;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .bnote{font-weight:bold;font-style: italic;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .vrs{}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sblock_labels > .infs{}

.entry_v2 .sblocks > .sblock > .sblock_c > .scnt{margin-bottom:4px;overflow:hidden;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt:last-child{margin-bottom:0;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense{}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > *:last-child{margin-bottom:0;padding-bottom:0;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .sn_letter{font-weight:bold;float:left;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .sd{font-style:italic;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .bnote{font-weight:bold;font-style:italic;color:#000;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .slb{font-style:italic; color:#757575;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .sgram{}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .sgram > .sgram_internal{color:#009900;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .ssla{font-style:italic;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .def_text{ font-size: 110%; margin-bottom:0px;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .def_text > .bc{font-weight:bold;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .def_labels{margin-top:5px;padding-left:14px;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .def_labels > .wsgram{}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .def_labels > .wsgram > .wsgram_internal{color:#009900;}
.entry_v2 .sblocks > .sblock > .sblock_c > .scnt > .sense > .def_labels > .sl{font-style:italic;}

/*view: verbal illustration*/
.entry_v2 .vis_w{padding-left:0em;}
.entry_v2 .vis_w > .vis{list-style-position:inside;list-style-position:outside;overflow:hidden;}
.entry_v2 .vis_w > .vis > .vi{padding:0;color:teal;}
.entry_v2 .vis_w > .vis > .vi::before {content: "●"; color:#5FB68C; display: inline; font-size: 60%}
.entry_v2 .vis_w > .vis > .vi > .vi_content{color:#000;margin-left:.2em; display: inline;}

/*view: dros*/
.entry_v2 > .dros{margin-bottom:.5em;}
.entry_v2 > .dros > .dro{margin-bottom:0.4em;padding-left:0.4em;}
.entry_v2 > .dros > .dro:last-child{margin-bottom:0;}
.entry_v2 > .dros > .dro > .dro_line{margin-left:-0.4em;}
.entry_v2 > .dros > .dro > .dro_line > *{vertical-align: middle}
.entry_v2 > .dros > .dro > .dro_line > .dre{display:inline;font-weight:bold;padding:0;margin:0;font-size:110%;color:#032952;}
.entry_v2 > .dros > .dro > .dro_line > .gram > .gram_internal{color:#009900; font-weight: bold; font-style:italic;}
.entry_v2 > .dros > .dro > .dro_line > .sl{font-style:italic; color:#009900;}
.entry_v2 > .dros > .dro > .dro_line > .rsl{font-style:italic;}
.entry_v2 > .dros > .dro > .dxs{margin-top:0.3em;display:block;}

/*view: uros*/
.entry_v2 > .uros{margin-bottom:.5em;}
.entry_v2 > .uros > .uro{margin-bottom:0.4em;padding-left:0.8em;}
.entry_v2 > .uros > .uro:last-child{margin-bottom:0;}
.entry_v2 > .uros > .uro > .uro_line{margin-left:-0.8em;}
.entry_v2 > .uros > .uro > .uro_line > *{vertical-align: middle}
.entry_v2 > .uros > .uro > .uro_line > .ure{display:inline;font-weight:bold;padding:0;margin:0;font-size:inherit;margin-right:0.5em}
.entry_v2 > .uros > .uro > .uro_line > .gram > .gram_internal{color:#009900;}
.entry_v2 > .uros > .uro > .uro_line > .lb{font-style: italic;}
.entry_v2 > .uros > .uro > .uro_line > .sl{font-style: italic;}
.entry_v2 > .uros > .uro > .uro_line > .fl{color:#8f0610;font-style:italic;font-weight: bold;}
.entry_v2 > .uros > .uro > .uro_def{margin:0.5em 0 0 0;}
.entry_v2 > .uros > .uro > .uro_def:first-child{margin-top:0;}
.entry_v2 > .uros > .uro > .uro_def > *:first-child{margin-top:0;}

/*view: inline synonyms*/
.entry_v2 .isyns{}
.entry_v2 .isyns > .bc{font-weight:bold;}
.entry_v2 .isyns > .isyn_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .isyns > .isyn_link sup{font-size:50%;}
.entry_v2 .isyns > .syn_sn{}
/*view: cognate cross entries*/
.entry_v2 > .cxs{margin-top:.5em;margin-bottom:.3em;}
.entry_v2 > .cxs .cx_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 > .cxs .cx_link sup{font-size:50%;}
.entry_v2 > .cxs .cl{font-style:italic;}

/*view: directional cross entries*/
.entry_v2 .dxs{color: #8F0610;}
.entry_v2 .dxs.dxs_nl{margin-bottom:.5em;}
.entry_v2 .dxs .dx{color: #8F0610;}
.entry_v2 .dxs .dx .dx_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .dxs .dx .dx_link sup{font-size:50%;}
.entry_v2 .dxs .dx .dx_span{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .dxs .dx .dx_span sup{font-size:50%;}
.entry_v2 .dxs .dx .dx_sn{}
.entry_v2 .dxs .dx .dx_ab{font-style:italic;}
.entry_v2 .dxs .dx .dx_tag{font-style:italic;}

/*view: cas*/
.entry_v2 .cas{margin-top:6px;}
.entry_v2 .cas > .cas_h{}
.entry_v2 .cas > .ca_prefix{font-style:italic;}
.entry_v2 .cas > .ca_text{font-style:italic;}

/*view: usage paragraphs*/
.entry_v2 .usage_par{padding:0.3em 0.7em;border:1px solid #ccc;margin-bottom:.5em;}
.entry_v2 .usage_par > .usage_par_h{font-weight:bold;}
.entry_v2 .usage_par > .ud_text{text-align:justify;}
.entry_v2 .usage_par > *{margin-bottom:0.3em;}
.entry_v2 .usage_par > *:last-child{margin-bottom:0;}

/*view: synref*/
.entry_v2 .synref_block{}
.entry_v2 .synref_h1{font-weight: bold;}
.entry_v2 .synref_h2{}
.entry_v2 .synref_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .synref_link sup{font-size:50%;}

/*view: usageref*/
.entry_v2 .usageref_block{}
.entry_v2 .usageref_block > .usageref_h1{font-weight: bold;}
.entry_v2 .usageref_block > .usageref_h2{}
.entry_v2 .usageref_block > .usageref_link{font-variant:small-caps;font-size:1.1em;line-height:1;}
.entry_v2 .usageref_block > .usageref_link sup{font-size:50%;}

/***************** 2016/2/6 ******************/

/* 此处修改例句颜色 */
.entry_v2 .vis_w > .vis > .vi > .vi_content {margin-left: .3em; color: #369; /* #3399FF; #0199FF; #3377FF; #398597; #1E90FF;*/}

/* 例句中的短语是否加粗、倾斜 */
.mw_spm_phrase {font-weight: bold; font-style: italic;color: #032952;}
.mw_spm_it {font-weight: bold; font-style: italic; color: #0B5BC4;}

/* 关闭无关内容的显示 */
.save_faves {display: none;}
.vi_more{display: none;}
.jumpcontent{display:none;}

/***************** 2016/2/15 ******************/

/* 分割线 */
.sms {
	padding-top: 12px;
	border-top: 1px dashed #ccc;
	clear: both;
}

/* 要跳转到的主词条 */
.realmainentry {font-weight: bold;}

.xml-hide-o_list{
	display: none;
}
.o_count{
-webkit-touch-callout: none; /* iOS Safari */
-webkit-user-select: none;   /* Chrome/Safari/Opera */
-khtml-user-select: none;    /* Konqueror */
-moz-user-select: none;      /* Firefox */
-ms-user-select: none;       /* IE/Edge */
user-select: none;           /* non-prefixed version, currently not supported by any browser */
}

ul {
display: block;
list-style-type: none;
-webkit-margin-before: 0;
-webkit-margin-after: 0;
-webkit-margin-start: 0;
-webkit-margin-end: 0;
-webkit-padding-start: 0;
}

a.play_pron {
	/*color:#D40218;font-size:167%;margin-left:7px;*/
    padding: 1em;
    background-size: 1.45em;
    background-image: url(C:/Users/14708/PycharmProjects/pythonProject2/sound.png);
    background-repeat: no-repeat;
    background-position: center;
    color: red; /* 设置文本颜色 */
}


.entry.entry_v2.boxy {
}

.usage_par,.sense .usage_par,.synpar {
    position: relative;
    margin:2em 0 1em;
    padding: 1em .7em .7em;
    border: 1px solid #ccc;
    border-radius: .2em;
}
.syn_par_h,
.usage_par_h {
    position: absolute;
    height: 1.4em;
    left: 0em;
    top: -1.6em;
    padding:0 1em;
    border-radius: .7em;
    background: #0b5bc4;
    font-size: 100%;
    line-height: 1.5em;
    color:white;
    font-weight: 700;
}

.usage_par_h .mw_zh, .syn_par_h .mw_zh {
    font-size: 90%;
    color:white;
}

.vi_content .mw_spm_aq .mw_zh {
    font-size: 85%;
    color:black;
    display:inline;
}

.def_text .mw_zh {
	margin-left: .3em;
    font-size: 90%;
    color:darkred;
}

/* 中文例句 */
.vi_content .mw_zh {
    font-size: 90%;
    color:#193031;
    display:block;
}
.vi_content {margin-left: .3em;color: #369;}
.v_label{color: #009900;}
.v_text{font-size:110%; font-weight: bold; color:#032952;}
.sl{font-style:italic; color:#009900;}

/* 图片缩放 */
.entryimg{max-height:5em;border:1px solid #ccc}
.entryimg.is-active{max-height:414px}
img{border:1px solid #ddd;padding-top:0px;max-width:100%;}

.all-entry {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 10px;
    margin-top: 25px;
    position: relative;
}
.custom-checkbox {
    transform: scale(1.5); /* 放大单选框 */
    margin-right: 10px; /* 设置单选框之间的间距 */
}
</style>
</head>
'''
audio_path_abc = ""
partSubAtCurrent = ""
video_name = ""
value_f = 0
value_b = 0
selected_text = ""
audio_fileName = ""


class MyWindow(QMainWindow):
    video_length = 0
    media_player = None
    open_subs = None
    open_subs_zh = None
    winfo_x = None
    win_size_x = None
    winfo_y = None
    value_f = 0
    value_b = 0
    ChipVideoDelay_signal = pyqtSignal()
    play_button = None

    def __init__(self):
        super().__init__()
        self.export_instance = None
        self.words_text_item = None
        self.white_rect = None
        self.aspect_ratio = None
        self.font = None
        self.media_width = None
        self.media_height = None
        self.auto_translator_script = None
        self.timer = None
        self.copy_subs = None
        self.current_sub = None
        self.auto_translator_off = None
        self.auto_translator_on = None
        self.text_document_zh_trans = None
        self.srt_text_item_zh_trans = None
        self.text_document_zh = None
        self.subs_zh = None
        self.srt_text_item_zh = None
        self.spinbox_ins_b = None
        self.spinbox_ins_f = None
        self.settings = None
        self.value_b = 0
        self.value_f = 0
        self.main_window = None
        self.subs_modified = None
        self.word_phrase_current_list = None
        self.proxy_button = None
        self.button = None
        self.items = None
        self.listWidget = None
        self.text_document = None
        self.srt_text_item = None
        self.subs = None
        self.subtitle_zh = None
        self.subtitle_en = None
        self.video_item = None
        self.scene = None
        self.view = None
        self.play_button1 = None
        self.video_proses = None
        self.play_button = None
        self.isTranslator = False

        self.selected_file = ""

        self.media_player = None
        MyWindow.win_size_x = self.width()
        MyWindow.winfo_x = self.pos().x()

        self.initUI()

        self.load_settings()

        self.old_win_width = self.size().width()

    def initUI(self):
        # region 创建打开视频窗口菜单
        open_menubar = self.menuBar()
        open_action = QAction('打开视频', self)
        open_action.triggered.connect(self.openVideo)
        open_menubar.addAction(open_action)  # 添加动作到菜单栏

        # 创建一个带有次级菜单的菜单项
        tool_action = QAction('工具', self)
        just_subs = QAction('调整字幕时间', self)
        just_videoChip = QAction('调整视频截取时间', self)
        assvert_action = QAction('ass双语字幕分割成srt文件', self)
        auto_translator = QAction('机器翻译字幕', self)
        self.auto_translator_on = QAction('开启', self)
        export_action = QAction('导出单词', self)
        github_action = QAction('关于', self)

        self.auto_translator_on.setCheckable(True)
        self.auto_translator_off = QAction('关闭', self)
        self.auto_translator_off.setCheckable(True)
        group = QActionGroup(self)
        group.addAction(self.auto_translator_off)
        group.addAction(self.auto_translator_on)

        just_subs.triggered.connect(self.apply_time_shift)
        just_videoChip.triggered.connect(self.chip_video_delay)
        assvert_action.triggered.connect(self.browse_and_convert)
        self.auto_translator_on.triggered.connect(self.on_translator)
        self.auto_translator_off.triggered.connect(self.off_translator)
        export_action.triggered.connect(self.export_words)
        github_action.triggered.connect(self.git_web)

        # 创建次级菜单
        sub_menu = QMenu()
        sub_menu.addAction(just_subs)
        sub_menu.addAction(just_videoChip)
        sub_menu.addAction(assvert_action)
        sub_menu.addAction(auto_translator)

        # 创建机器翻译子菜单
        sub_menu_trans = QMenu()
        sub_menu_trans.addAction(self.auto_translator_on)
        sub_menu_trans.addAction(self.auto_translator_off)

        # 将次级菜单添加到 "打开" 菜单项
        tool_action.setMenu(sub_menu)
        auto_translator.setMenu(sub_menu_trans)
        open_menubar.addAction(tool_action)
        open_menubar.addAction(export_action)
        open_menubar.addAction(github_action)

        # endregion

        # region 创建组件，播放按钮,进度条，布局容器
        # 创建播放/暂停按钮
        self.play_button = QPushButton('播放/暂停', self)
        MyWindow.play_button = self.play_button
        self.play_button.clicked.connect(self.togglePlayPause)
        self.play_button.resize(self.size().width(), 20)

        # 创建进度条
        self.video_proses = VideoContainer(self)

        # 创建布局并将播放按钮添加到布局中
        layout = QVBoxLayout()

        layout.addWidget(self.video_proses)

        layout.addWidget(self.play_button)

        # 创建一个容器窗口并将布局设置为容器窗口的布局
        container = QWidget()
        container.setLayout(layout)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container.setFixedHeight(100)
        # endregion

        # 设置容器2的大小策略为固定（Fixed），并指定固定宽度和高度
        self.scene = QGraphicsScene()
        self.view = MyGraphicsView(self.scene, self)
        self.view.setCacheMode(QGraphicsView.CacheBackground)
        self.view.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        # 创建一个背景刷子并设置背景颜色
        background_brush = QBrush(QColor(100, 100, 100))  # 使用灰色作为背景颜色
        self.view.setBackgroundBrush(Qt.black)

        # self.view.resize(779, 455)
        # self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setFrameShape(0)
        self.video_item = QGraphicsVideoItem()
        # self.video_item.nativeSizeChanged.connect(self.handleNativeSizeChanged)
        # self.view.fitInView(self.video_item, Qt.KeepAspectRatio)
        self.video_item.setSize(QSizeF(self.view.size().width(), self.view.size().height() - 5))
        rect_item = QGraphicsRectItem(self.view.rect().x(), self.view.rect().y(), self.view.rect().width(),
                                      self.view.rect().height() - 3)
        # 添加一个白色矩形
        # self.white_rect = QGraphicsRectItem()
        # self.white_rect.setBrush(Qt.white)
        # self.white_rect.hide()

        rect_item.setBrush(QColor(0, 0, 0))

        self.srt_text_item = QGraphicsTextItem()
        self.srt_text_item_zh = QGraphicsTextItem()
        self.srt_text_item_zh_trans = QGraphicsTextItem()
        self.words_text_item = QGraphicsTextItem()
        # self.words_text_item.setParentItem(self.white_rect)
        # 把QGraphicsVideoItem对象放到view类里
        self.view.text_item = self.srt_text_item
        self.text_document = QTextDocument()
        self.text_document_zh = QTextDocument()
        self.text_document_zh_trans = QTextDocument()
        self.text_document.setTextWidth(500)  # 设置文本的宽度，当文本到达这个宽度时会自动换行
        self.text_document_zh.setTextWidth(500)
        self.text_document_zh_trans.setTextWidth(500)
        text_option = QTextOption()
        text_option.setWrapMode(QTextOption.WordWrap)  # 设置为单词边界换行
        text_option.setAlignment(Qt.AlignCenter)  # 设置文本居中对齐
        self.text_document.setDefaultTextOption(text_option)
        self.text_document_zh.setDefaultTextOption(text_option)
        self.text_document_zh_trans.setDefaultTextOption(text_option)

        # 将文本文档设置为文本项的内容
        self.srt_text_item.setDocument(self.text_document)
        self.srt_text_item_zh.setDocument(self.text_document_zh)
        self.srt_text_item_zh_trans.setDocument(self.text_document_zh_trans)
        self.srt_text_item.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # 设置文本项的包裹模式为在单词边界或任何位置换行
        # self.srt_text_item.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.font = QFont()  # 创建字体对象
        self.font.setBold(True)
        self.font.setPointSize(17)  # 设置字体大小
        font_zh = QFont()  # 创建字体对象
        font_zh.setPointSize(12)  # 设置字体大小
        self.srt_text_item.setFont(self.font)  # 应用字体到文本项
        self.srt_text_item_zh.setFont(font_zh)  # 应用字体到文本项
        self.srt_text_item_zh_trans.setFont(font_zh)  # 应用字体到文本项

        text_color1 = QColor(255, 255, 0)  # 白色文本颜色
        text_color = QColor(255, 255, 255)  # 白色文本颜色
        self.srt_text_item.setDefaultTextColor(text_color)
        self.srt_text_item_zh.setDefaultTextColor(text_color)
        self.srt_text_item_zh_trans.setDefaultTextColor(text_color1)

        # 创建文本项的阴影效果
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setColor(QColor(0, 0, 0))  # 阴影颜色（黑色）
        # shadow.setBlurRadius(8)  # 模糊半径
        # self.srt_text_item.setGraphicsEffect(shadow)
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setBlurRadius(0)
        shadowEffect.setColor(Qt.black)
        shadowEffect.setOffset(1, 1)
        self.srt_text_item.setGraphicsEffect(shadowEffect)

        button = QPushButton("生\n词\n本")
        button.setFixedSize(30, 100)

        self.scene.addItem(self.video_item)
        self.scene.addItem(self.srt_text_item)
        self.scene.addItem(self.srt_text_item_zh)
        self.scene.addItem(self.srt_text_item_zh_trans)
        self.scene.addItem(self.words_text_item)

        self.proxy_button = self.scene.addWidget(button)

        # 创建一个布局来容纳视频窗口和按钮容器
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.view)
        # main_layout.addStretch()
        main_layout.addWidget(container)

        # 创建一个主窗口部件来容纳视频和按钮
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        # self.setLayout(main_layout)

        # region 创建侧边栏和连接槽函数
        # 创建侧边栏和悬浮按钮
        self.items = QDockWidget('Dockable', self)
        self.items.setTitleBarWidget(QWidget())  # 隐藏标题栏
        self.items.setHidden(True)  # 默认情况下隐藏
        self.items.setFixedSize(177, self.height())
        # 创建按钮并添加到侧边栏
        container_widget = QWidget(self.items)
        # 创建一个图标
        icon = QIcon("a_zSort.png")  # 替换为实际图标文件的路径

        button_side = QPushButton('本集单词', self.items)
        button_side_del = QPushButton('删除单词', self.items)
        button_sort = QPushButton('排序', self.items)
        # 设置按钮的图标
        button_sort.setIcon(icon)

        button_side.clicked.connect(self.showCurrentWords)
        button_side_del.clicked.connect(self.deleted_word)
        button_sort.clicked.connect(self.sortItems)

        self.listWidget = QListWidget()
        layout = QVBoxLayout(container_widget)
        # layout.addWidget(label, 0, Qt.AlignTop)

        layout.addWidget(button_sort)
        layout.addWidget(self.listWidget)
        layout.addWidget(button_side)
        layout.addWidget(button_side_del)

        container_widget.setLayout(layout)

        self.items.setWidget(container_widget)
        self.items.setFloating(False)
        # 创建按钮来显示/隐藏侧边栏

        self.setMouseTracking(True)

        button.clicked.connect(self.toggle_sidebar)
        self.listWidget.itemDoubleClicked.connect(self.creat_small_video)
        # 连接右击事件到自定义的上下文菜单处理函数
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.showContextMenu)

        self.addDockWidget(Qt.RightDockWidgetArea, self.items)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadSubtitle)

        # 创建快捷键
        shortcut_seek_forward = QShortcut(QKeySequence(Qt.Key_Right), self)
        shortcut_seek_backward = QShortcut(QKeySequence(Qt.Key_Left), self)
        shortcut_increase_volume = QShortcut(QKeySequence(Qt.Key_Up), self)
        shortcut_decrease_volume = QShortcut(QKeySequence(Qt.Key_Down), self)

        # 连接快捷键到相应的槽函数
        shortcut_seek_forward.activated.connect(self.seek_forward)
        shortcut_seek_backward.activated.connect(self.seek_backward)
        shortcut_increase_volume.activated.connect(self.increase_volume)
        shortcut_decrease_volume.activated.connect(self.decrease_volume)
        self.ChipVideoDelay_signal.connect(self.load_settings)
        # endregion

    def loadSubtitle(self):
        if MyWindow.media_player is not None:
            if self.isTranslator:
                self.srt_text_item_zh_trans.setVisible(True)
                position = MyWindow.media_player.position()
                current_sub = None
                self.current_sub = None
                # 加载修改的英文字幕
                if self.subs is not None:
                    for sub in self.subs:
                        if sub.start.ordinal <= position <= sub.end.ordinal:
                            current_sub = sub
                            break

                if current_sub:
                    # 设置翻译字幕的位置，如果中文字幕存在就在其下面，反之，在顶部
                    current_sub_zh_trans = self.translate_text(current_sub.text)
                    self.text_document_zh_trans.setPlainText(current_sub_zh_trans)
                    width = self.srt_text_item_zh_trans.boundingRect().width()
                    parentWidth = self.view.size().width()
                    x = (parentWidth - width) / 2
                    if self.subs_zh is not None:
                        height = self.srt_text_item_zh.boundingRect().height()
                        self.srt_text_item_zh_trans.setPos(x, height)

                    else:
                        self.srt_text_item_zh_trans.setPos(x, 0)
                else:
                    self.text_document_zh_trans.setHtml("")
            else:
                self.srt_text_item_zh_trans.setVisible(False)

    def git_web(self):
        webbrowser.open("https://cn.bing.com/search?q=" + self.selected_text)

    def showContextMenu(self, event):
        # 创建一个上下文菜单
        contextMenu = QMenu(self)

        # 在上下文菜单中添加一些操作
        action1 = QAction("跳转到视频处", self)
        action2 = QAction("删除", self)

        contextMenu.addAction(action1)
        action1.triggered.connect(self.jump_word_In_Video)
        contextMenu.addAction(action2)

        # 显示上下文菜单在鼠标右击的位置
        contextMenu.exec_(self.listWidget.mapToGlobal(event))

    def jump_word_In_Video(self):

        selected_item = self.listWidget.currentItem()
        if selected_item:
            # 获取当前选定项目的文本
            content = selected_item.text()
            split_result = content.split('   ')

            if self.subs_modified is not None:
                if " " not in split_result[1]:
                    print(1)
                    for subs in self.subs_modified:
                        if split_result[1].lower() in subs.text.lower():
                            MyWindow.media_player.setPosition(subs.start.ordinal)
                else:
                    print(split_result[1])
                    for subs1 in self.subs:
                        good = subs1.text.replace("\n", " ")

                        if split_result[1].lower() in good.lower():
                            MyWindow.media_player.setPosition(subs1.start.ordinal)

    def sortItems(self):
        # 获取项目列表并按字母顺序排序
        items = [self.listWidget.item(i) for i in range(self.listWidget.count())]
        new_list = []
        items.sort(key=lambda x: x.text().split('   ')[1].lower())
        for item in items:
            new_list.append(item.text())

        # 清空列表并重新添加排序后的项目
        self.listWidget.clear()
        for item in new_list:
            self.listWidget.addItem(item)

    def showCurrentWords(self):
        if MyWindow.media_player is not None:
            items_to_delete = []

            # 获取 QListWidget 中的所有项目
            item_count = self.listWidget.count()
            for index in range(item_count):
                item = self.listWidget.item(index)
                num, word1 = item.text().split('   ')
                if word1.lower() not in [word.lower() for word in self.word_phrase_current_list]:
                    items_to_delete.append(index)

            # 从 QListWidget 中删除项目，注意要从后往前删除
            for index in reversed(items_to_delete):
                self.listWidget.takeItem(index)

    def deleted_word(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            # 获取当前选定项目的文本
            content = selected_item.text()
            split_result = content.split('  ')
            with open("markWordList.csv", "r", encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
            # 删除指定索引的条目
            sga = int(split_result[0]) - 1
            del rows[int(split_result[0]) - 1]
            for index1, row1 in enumerate(rows[sga:], start=sga):
                rows[index1][0] = str(index1 + 1)  # 更新索引字段，从1开始计数
            with open("markWordList.csv", "w", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            self.listWidget.takeItem(self.listWidget.row(selected_item))
            print("已删除")

    def operate_subtitle(self):

        word_current_list = []

        phrase_current_list = []
        # 获取生词本里的短语元组，不包含单词
        words_phrase = set()
        # 获取生词本里的单词元组，不包含短语
        words_set = set()
        if os.path.exists('markWordList.csv'):
            with open("markWordList.csv", "r", newline="", encoding="utf-8") as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    if len(row) > 2:  # 确保行中有足够的字段
                        abc = row[1].split()
                    if len(abc) > 1:
                        words_phrase.add(row[1])
                    if len(abc) == 1:
                        words_set.add(row[1])

            if self.subtitle_en is not None:
                self.copy_subs = copy.deepcopy(self.subs)
                for sub in self.copy_subs:  # 遍历每一条字幕
                    text = sub.text  # 获取字幕文本
                    words_in_text = text.split()  # 把文本按空格分割成单词列表
                    for i, word in enumerate(words_in_text):  # 遍历每一个单词及其索引
                        word_nof = word.rstrip(',.?!"\'')
                        if word_nof.lower() in [word2.lower() for word2 in words_set]:  # 如果单词在a文件中
                            words_in_text[i] = "<font color=\"#00ff00\">" + word + "</font>"  # 给单词加上<font>标签和颜色代码
                            word_current_list.append(word_nof)  # 添加找到的字幕生词到列表
                    sub.text = " ".join(words_in_text)  # 把单词列表重新拼接成文本

                    temp = sub.text
                    temp_fail = sub.text
                    isFound = True  # 用于标记是否找到匹配的情况
                    # 每次循环处理一个短语words_phrase1
                    for words_phrase1 in words_phrase:
                        # 把一个短语分割成独立单词列表split_phrase
                        split_phrase = words_phrase1.split()
                        b = 0
                        # 每次循环处理一个单词列表中的单词phrase
                        temp_split_list = temp.split()
                        for i, phrase in enumerate(split_phrase):
                            for j, word in enumerate(temp_split_list[b:]):  # 遍历每一个单词及其索引
                                word_nof = word.rstrip(',.?!"\'')
                                if phrase.lower() == word_nof.lower():
                                    d_w = "<font color=\"#ff0000\">" + word + "</font>"  # 给单词加上<font>标签和颜色代码
                                    temp_split_list[j + b] = d_w
                                    b = j + b
                                    isFound = True
                                    break
                                else:
                                    isFound = False

                                    continue

                            if i + 1 == len(split_phrase):
                                if isFound:
                                    sub.text = " ".join(temp_split_list)  # 把单词列表重新拼接成文本
                                    temp = temp_fail
                                    phrase_current_list.append(words_phrase1)  # 添加找到的字幕生词到列表

                            if not isFound:
                                temp = temp_fail
                                break

                self.word_phrase_current_list = word_current_list + phrase_current_list
                print(phrase_current_list)
                self.copy_subs.save("templating.srt", encoding='utf-8')  # 保存srt文件
                print("templating.srt创建")
                self.subs_modified = pysrt.open("templating.srt")
            else:
                print("字幕不存在")
                return None
        else:
            return None

    def pop_window(self):
        # 向列表中添加一些内容
        if os.path.exists('markWordList.csv'):
            words_list = []  # 创建一个空集合
            with open("markWordList.csv", "r", newline="", encoding="utf-8") as csvfile:
                csvreader = csv.reader(csvfile)
                # next(csvreader)  # 跳过表头行
                for row in csvreader:
                    if len(row) > 2:  # 确保行中有足够的字段
                        index = row[0]
                        word = row[1]
                        sentence_row = row[2]
                        self.listWidget.addItem("{}   {}".format(index, word))

        # 创建单词播放窗口

    def creat_small_video(self):
        # 获取当前选中的索引
        index = self.listWidget.currentRow()
        # 获取当前选中的内容
        content = self.listWidget.currentItem().text()
        split_result = content.split('  ')

        if len(split_result) >= 2:
            index = split_result[0]
            word = split_result[1]

        else:
            print("收藏单词条目过短.")

        # 插入字符串"Hello World"到文本框中
        if os.path.exists('markWordList.csv'):
            with open("markWordList.csv", "r", newline="", encoding="utf-8") as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    if index == row[0]:
                        # var = tk.StringVar()
                        # var.set(row[2])
                        sssstence = row[2]
                        word_definite = row[3]
                        video_read_path = row[5]

        class CustomMainWindow(QMainWindow):
            def __init__(self, word_definite, word_video):
                super().__init__()
                self.setGeometry(MyWindow.winfo_x + MyWindow.win_size_x, MyWindow.winfo_y + 50, 300, 600)

                central_widget = QWidget(self)
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                video_widget = QVideoWidget(self)
                video_widget.setFixedSize(300, 240)  # Video area size
                layout.addWidget(video_widget)

                # Add QLabel to display a sentence with a width of 40
                sentence_label = QLabel(sssstence)
                sentence_label.setFixedSize(277, 50)
                sentence_label.setAlignment(Qt.AlignCenter)
                sentence_label.setWordWrap(True)
                sentence_label.setTextInteractionFlags(
                    Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)  # Allow text selection
                layout.addWidget(sentence_label)

                web_engine_view = QWebEngineView(self)
                layout.addWidget(web_engine_view)

                # Load HTML content
                web_engine_view.setHtml(word_definite + cssfile)

                # Set layout for the central widget
                central_widget.setLayout(layout)
                # Create QMediaPlayer and load local video
                self.media_player = QMediaPlayer()
                self.media_player.setVideoOutput(video_widget)

                # 加载视频
                script_directory = os.path.dirname(os.path.abspath(__file__))
                subfolder_path = os.path.join(script_directory, "media\\" + video_read_path)
                video_path = subfolder_path
                media_content = QMediaContent(QUrl.fromLocalFile(video_path))
                self.media_player.setMedia(media_content)
                self.media_player.play()

                central_widget.setLayout(layout)

        self.main_window = CustomMainWindow(word_definite, word)
        self.main_window.show()

    def trancing_word(self):
        if self.current_sub is not None:

            # 使用正则表达式匹配<font>标签中的文本内容
            match = re.search(r'<font[^>]*>(.*?)</font>', self.current_sub.text)

            if match:
                matched_text = match.group(1).rstrip(',.?!"\'')
                print(matched_text)
                # 获取 QListWidget 中的所有项目
                item_count = self.listWidget.count()
                for index in range(item_count):
                    item = self.listWidget.item(index)
                    num, word = item.text().split('   ')
                    if matched_text.lower() in word.lower():
                        item.setSelected(True)
                        self.listWidget.scrollToItem(item)


            else:
                print("未找到匹配的内容")

    def toggle_sidebar(self):
        # 显示/隐藏侧边栏
        if self.main_window is not None:
            self.main_window.deleteLater()
            self.main_window = None

        self.listWidget.clear()
        self.pop_window()
        if self.items.isHidden():
            self.resize(self.width() + self.items.width(), self.height())
            self.items.setHidden(False)
            self.items.setFixedSize(177, self.height() - 126)
            MyWindow.winfo_x = self.pos().x()
            MyWindow.win_size_x = self.width()
            MyWindow.winfo_y = self.pos().y()

            self.trancing_word()
        else:
            self.items.setHidden(True)
            self.resize(self.width() - self.items.width(), self.height())
            MyWindow.winfo_x = self.pos().x()
            MyWindow.win_size_x = self.width()

    def seek_forward(self):
        MyWindow.media_player.setPosition(MyWindow.media_player.position() + 5000)  # 前进5秒

    def seek_backward(self):
        MyWindow.media_player.setPosition(MyWindow.media_player.position() - 5000)  # 后退5秒

    def increase_volume(self):
        current_volume = MyWindow.media_player.volume()
        MyWindow.media_player.setVolume(max(current_volume + 10, 100))  # 增加音量10%

    def decrease_volume(self):
        current_volume = MyWindow.media_player.volume()
        MyWindow.media_player.setVolume(max(current_volume - 10, 0))  # 减少音量10%

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.media_player is not None:
                if self.media_player.state() == QMediaPlayer.PlayingState:
                    self.media_player.pause()
                    self.play_button.setText('播放')
                else:
                    self.media_player.play()
                    self.play_button.setText('暂停')
        super().keyPressEvent(event)

    def showEvent(self, event):
        # ensure that the update only happens when showing the window
        # programmatically, otherwise it also happen when unminimizing the
        # window or changing virtual desktop
        # 判断事件是否为程序外部触发，是的话返回True
        if not event.spontaneous():
            pb_height = self.proxy_button.boundingRect().height()
            self.proxy_button.setPos(self.view.width() - 33, (self.view.height() - pb_height) / 2)

    def resizeEvent(self, event):
        if event.spontaneous():
            # 设置侧边栏的高度与窗口相同
            self.items.setFixedSize(177, self.height() - 126)

            MyWindow.win_size_x = self.size().width()

            print("Current Sizes:")
            print(f"View Size: {self.view.size().width()} x {self.view.size().height()}")
            print(
                f"videoItem Size: {self.video_item.boundingRect().width()} x {self.video_item.boundingRect().height()}")
            print(f"window Size: {self.width()} x {self.height()}")
            print(f"scene Size: {self.scene.sceneRect()}")

            # region 让字幕位置总是在view的下方
            width = self.srt_text_item.boundingRect().width()
            width_zh = self.srt_text_item_zh.boundingRect().width()
            height = self.srt_text_item.boundingRect().height()
            parentWidth = self.view.size().width()
            parentHeight = self.view.size().height()
            x = (parentWidth - width) / 2
            x_zh = (parentWidth - width_zh) / 2
            y = parentHeight - height
            self.srt_text_item.setPos(x, y)
            self.srt_text_item_zh.setPos(x_zh, 0)
            if self.subs_zh is not None:
                self.srt_text_item_zh_trans.setPos(x_zh, 35)
            else:
                self.srt_text_item_zh_trans.setPos(x_zh, 0)

            # self.view.centerOn(self.video_item)
            # endregion

            # region 改变字体大小和字幕宽度
            move_step = self.size().width() - 658
            if move_step > 0:
                font_size = move_step // 80
                text_width = move_step // 2
                self.font.setPointSize(17 + font_size)  # 设置字体大小
                self.srt_text_item.setFont(self.font)
                self.text_document.setTextWidth(500 + text_width)
            self.old_win_width = self.size().width()
            # endregion

            # region 让视频等比例放大

            # 获取视频的原始宽高比例
            if self.aspect_ratio is not None:
                # 获取view的新宽度
                new_width = self.view.size().width()

                # 根据新的宽度计算新的高度以保持比例
                new_height = new_width / self.aspect_ratio

                # 设置视频项的大小
                self.video_item.setSize(QSizeF(new_width, new_height))

            # 计算 QGraphicsVideoItem 的位置，使其位于 QGraphicsScene 的中心
            item_x = 0
            item_y = (self.view.size().height() - self.video_item.boundingRect().height()) / 2

            # 设置 QGraphicsVideoItem 的位置
            self.video_item.setPos(item_x, item_y)
            # endregion

            pb_height = self.proxy_button.boundingRect().height()
            self.proxy_button.setPos(self.view.width() - 33, (self.view.height() - pb_height) / 2)
        else:
            print("This is not a spontaneous event.")

        super().resizeEvent(event)

    def openVideo(self):
        global video_name
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # 可以选择只读文件
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("视频文件 (*.mp4 *.mkv *.avi);;所有文件 (*)")
        selected_file, _ = file_dialog.getOpenFileName(
            None, "选择视频文件", "", "视频文件 (*.mp4 *.mkv *.avi);;所有文件 (*)", options=options)

        if selected_file:
            video_name = selected_file
            self.selected_file = selected_file

            if ".mp4" in selected_file:
                self.subtitle_en = selected_file.replace(".mp4", ".srt")
                self.subtitle_zh = selected_file.replace(".mp4", ".zh.srt")
            if ".mkv" in selected_file:
                self.subtitle_en = selected_file.replace(".mkv", ".srt")
                self.subtitle_zh = selected_file.replace(".mkv", ".zh.srt")
            if os.path.exists(self.subtitle_en):
                print(f"英文字幕文件 '{self.subtitle_en}' exists.")
                encoding = self.detect_encoding(self.subtitle_en)
                self.subs = pysrt.open(self.subtitle_en, encoding=encoding)
                MyWindow.open_subs = self.subs
            else:
                print(f"英文字幕文件 '{self.subtitle_en}' does not exist.")

            if os.path.exists(self.subtitle_zh):
                print(f"Subtitle file '{self.subtitle_zh}' exists.")
                self.subs_zh = pysrt.open(self.subtitle_zh)
                MyWindow.open_subs_zh = self.subs_zh
            else:
                if self.subs_zh is not None:
                    self.subs_zh = None
                print(f"中文字幕文件 '{self.subs_zh}' does not exist.")

            self.VideoPlayer(selected_file)

            MyWindow.media_player = self.media_player

    def VideoPlayer(self, selected_file):
        if self.media_player:
            self.media_player.stop()
            self.media_player.setMedia(QMediaContent())  # 清除媒体内容
        # 将主窗口保存为实例变量
        self.media_player = QMediaPlayer()

        media_content = QMediaContent(QUrl.fromLocalFile(selected_file))  # 使用Qt.QUrl设置媒体内容

        self.media_player.setMedia(media_content)
        self.media_player.setVideoOutput(self.video_item)
        # 连接媒体元数据改变信号和槽函数

        self.media_player.mediaStatusChanged.connect(self.onMediaStatusChanged)

        self.media_player.play()
        self.operate_subtitle()
        self.media_player.setNotifyInterval(200)

        self.media_player.positionChanged.connect(self.position_changed)

    # 加载字幕，跟新进度条
    def position_changed(self, position):
        current_sub = None
        self.current_sub = None
        # 加载修改的英文字幕
        if self.subs_modified is not None:
            # # 记录循环开始时间
            # start_time = time.time()
            for sub in self.subs_modified:
                if sub.start.ordinal <= position <= sub.end.ordinal:
                    current_sub = sub
                    self.current_sub = current_sub
                    break

            # 加载中文字幕
            current_sub_zh = None
            if self.subs_zh is not None:
                for sub in self.subs_zh:
                    if sub.start.ordinal <= position <= sub.end.ordinal:
                        current_sub_zh = sub
                        break
            else:
                self.srt_text_item_zh.setVisible(False)
            # 更新标签的文本内容
            if current_sub:

                if current_sub_zh:
                    self.text_document_zh.setHtml(current_sub_zh.text)
                    width_zh = self.srt_text_item_zh.boundingRect().width()
                    height_zh = self.srt_text_item_zh.boundingRect().height()
                    parentWidth = self.view.size().width()
                    parentHeight = self.view.size().height()
                    x = (parentWidth - width_zh) / 2
                    y = height_zh
                    self.srt_text_item_zh.setPos(x, 0)
                else:
                    self.text_document_zh.setHtml("")

                self.text_document.setHtml(current_sub.text)

                width = self.srt_text_item.boundingRect().width()
                height = self.srt_text_item.boundingRect().height()
                parentWidth = self.view.size().width()
                parentHeight = self.view.size().height()
                x = (parentWidth - width) / 2
                y = parentHeight - height
                self.srt_text_item.setPos(x, y)
            else:
                self.text_document.setHtml("")

        # 进度条更新
        if MyWindow.media_player.duration() != 0:
            current_time = int(position / MyWindow.media_player.duration() * (self.video_proses.width() - 14))
            # if current_time < 0:
            #     current_time += 13
            VideoContainer.video_processor = QRect(QRect(7, 7, current_time, 39))
            self.update()

            # # 记录循环结束时间
            # end_time = time.time()
            #
            # # 计算执行时间
            # execution_time = end_time - start_time
            # print(f"循环执行时间: {execution_time} 秒")

        else:
            # 加载英文字幕
            if self.subs is not None:
                # 记录循环开始时间
                start_time = time.time()
                for sub in self.subs:
                    if sub.start.ordinal <= position <= sub.end.ordinal:
                        current_sub = sub
                        self.current_sub = current_sub
                        break

                # 更新标签的文本内容
                if current_sub:
                    self.text_document.setHtml(current_sub.text)
                else:
                    self.text_document.setHtml("")

                if current_sub:
                    if self.isTranslator:
                        # 在ThreadPoolExecutor中执行函数
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(self.translate_text, current_sub.text)
                            current_sub_zh_trans = future.result()
                        self.text_document_zh_trans.setPlainText(current_sub_zh_trans)
                else:
                    self.text_document_zh_trans.setHtml("")

    def onMediaStatusChanged(self, status):
        if status == QMediaPlayer.LoadedMedia:
            self.aspect_ratio = self.get_video_aspect_ratio(self.selected_file)
            if self.aspect_ratio is not None:
                print(f"Video Aspect Ratio: {self.aspect_ratio}")
                # region 让视频等比例放大

                # 获取view的新宽度
                new_width = self.view.size().width()

                # 根据新的宽度计算新的高度以保持比例
                new_height = new_width / self.aspect_ratio

                # 设置视频项的大小
                self.video_item.setSize(QSizeF(new_width, new_height))

                # 计算 QGraphicsVideoItem 的位置，使其位于 QGraphicsScene 的中心
                item_x = 0
                item_y = (self.view.size().height() - self.video_item.boundingRect().height()) / 2

                # 设置 QGraphicsVideoItem 的位置
                self.video_item.setPos(item_x, item_y)
                # endregion

                # region 改变字体大小和字幕宽度
                move_step = self.size().width() - 658
                font_size = move_step // 80
                text_width = move_step // 2
                self.font.setPointSize(17 + font_size)  # 设置字体大小
                self.srt_text_item.setFont(self.font)
                self.text_document.setTextWidth(500 + text_width)
                # endregion
            else:
                print("Failed to retrieve video aspect ratio.")

                # region 让视频等比例放大

                # 获取view的新宽度
                new_width = self.view.size().width()

                # 获取视频的原始宽高比例
                if self.aspect_ratio is not None:
                    video_width = self.media_width
                    video_height = self.media_height
                    aspect_ratio = video_width / video_height

                    # 根据新的宽度计算新的高度以保持比例
                    new_height = new_width / aspect_ratio

                    # 设置视频项的大小
                    self.video_item.setSize(QSizeF(new_width, new_height))

                # 计算 QGraphicsVideoItem 的位置，使其位于 QGraphicsScene 的中心
                item_x = 0
                item_y = (self.view.size().height() - self.video_item.boundingRect().height()) / 2

                # 设置 QGraphicsVideoItem 的位置
                self.video_item.setPos(item_x, item_y)
                # endregion

                # region 改变字体大小和字幕宽度
                move_step = self.size().width() - 658
                font_size = move_step // 80
                text_width = move_step // 2
                self.font.setPointSize(17 + font_size)  # 设置字体大小
                self.srt_text_item.setFont(self.font)
                self.text_document.setTextWidth(500 + text_width)
                # endregion

    def get_video_aspect_ratio(self, video_file):
        # 使用ffprobe命令获取视频信息，并将其输出为JSON格式
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                   'stream=width,height,r_frame_rate', '-of', 'json', video_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            try:
                # 解析JSON输出
                info = json.loads(result.stdout)
                # 提取视频宽度、高度和帧率信息
                width = info['streams'][0]['width']
                height = info['streams'][0]['height']
                frame_rate = eval(info['streams'][0]['r_frame_rate'])
                # 计算宽高比
                aspect_ratio = width / height
                return aspect_ratio
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error parsing ffprobe output: {e}")
                return None
        else:
            print(f"ffprobe error: {result.stderr}")
            return None

    def togglePlayPause(self):
        if self.media_player is not None:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.play_button.setText('播放')
            else:
                self.media_player.play()
                self.play_button.setText('暂停')

    def apply_time_shift(self):
        if self.subtitle_en is not None:
            # 创建自定义对话框
            dialog = TimeShiftDialog(self)

            # 显示对话框，并等待用户关闭
            result = dialog.exec_()

            # 如果用户点击了确认按钮
            if result == QDialog.Accepted:
                # 获取用户输入的秒数和毫秒数
                shift_seconds = dialog.seconds_spinbox.value()
                shift_milliseconds = dialog.milliseconds_spinbox.value()

                self.subs.shift(seconds=shift_seconds, milliseconds=shift_milliseconds)
                self.subs.save(self.subtitle_en)
                print("字幕已经调节")
                if self.operate_subtitle() is not None:
                    print("字幕已经调节")
                else:
                    print("字幕加载失败")

    def chip_video_delay(self):
        global value_f, value_b
        # 创建自定义对话框
        dialog = ChipVideoDelay(self)
        self.spinbox_ins_f = dialog.forward_spinbox
        self.spinbox_ins_b = dialog.backward_spinbox
        self.ChipVideoDelay_signal.emit()
        # 显示对话框，并等待用户关闭
        result = dialog.exec_()

        # 如果用户点击了确认按钮
        if result == QDialog.Accepted:
            # 获取用户输入的向前和向后偏移值（毫秒）

            forward_offset = dialog.forward_spinbox.value()
            backward_offset = dialog.backward_spinbox.value()

            self.value_f = int(forward_offset)
            MyWindow.value_f = self.value_f
            self.value_b = int(backward_offset)
            MyWindow.value_b = self.value_b

    def export_words(self):
        self.export_instance = ExportWindow()
        self.export_instance.show()

    def browse_and_convert(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # 可以选择只读文件
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("字幕文件 (*.ass);;所有文件 (*)")
        selected_file, _ = file_dialog.getOpenFileName(
            None, "选择视频文件", "", "字幕文件 (*.ass);;所有文件 (*)", options=options)

        if selected_file:
            file_name = os.path.basename(selected_file).replace(".ass", '')
            directory = os.path.dirname(selected_file) + '/'

            # Read ASS file
            ass_file_path = selected_file
            # 检测文件编码
            encoding = self.detect_encoding(ass_file_path)
            with open(ass_file_path, encoding=encoding) as f:
                ass_content = f.read()

            # Convert ASS to Chinese SRT
            chinese_srt_content = self.ass_to_srt(ass_content, "chinese")
            chinese_srt_file_path = f"{file_name}.zh.srt"
            with open(directory + chinese_srt_file_path, "w", encoding="utf-8") as f:
                f.write(chinese_srt_content)

            # Convert ASS to English SRT
            english_srt_content = self.ass_to_srt(ass_content, "english")
            english_srt_file_path = f"{file_name}.srt"

            with open(directory + english_srt_file_path, "w", encoding="utf-8") as f:
                f.write(english_srt_content)

            print(f"{directory + chinese_srt_file_path}, {directory + english_srt_file_path} 已经创建")

    def ass_to_srt(self, ass_content, language):
        srt_content = ""
        lines = ass_content.splitlines()
        subtitle_started = False
        subtitle_index = 1
        start_time = ""
        end_time = ""
        text = ""

        for line in lines:
            if subtitle_started:
                if line.startswith("Dialogue:"):
                    parts = line.split(",", maxsplit=9)
                    if len(parts) >= 10:
                        start_time = parts[1]
                        end_time = parts[2]
                        text = parts[9]

                        if language == "chinese":
                            if "\\N" in parts[9]:
                                srt_content += str(subtitle_index) + "\n" + start_time + " --> " + end_time + "\n" + \
                                               text.split("\\N")[0] + "\n\n"
                        elif language == "english":
                            if "\\N" in parts[9]:
                                en_text = re.sub(r'\{.*?\}', '', text.split("\\N")[1])
                                srt_content += str(subtitle_index) + "\n" + start_time + " --> " + end_time + "\n" + \
                                               en_text + "\n\n"

                        subtitle_index += 1
            elif line.strip() == "[Events]":
                subtitle_started = True

        return srt_content

    def detect_encoding(self, file_path):
        # 使用chardet检测文件编码
        detector = chardet.universaldetector.UniversalDetector()
        with open(file_path, 'rb') as f:
            for line in f:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        encoding = detector.result['encoding']
        return encoding

    def open_settings_dialog(self):
        # 打开设置对话框时，将当前的QSpinBox值设置为保存的设置值
        self.spin_box.setValue(self.settings.value('spin_box_value', 0, type=int))

    def translate_text(self, text):
        try:
            text = text.replace('\n', ' ')
            text = text.replace('"', ' ')
            # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
            cred = credential.Credential("AKIDeCakfMo11nOmvsc8QYUCfuvgBQP7ZyJU", "1mIYbPxGJ6g17yZu0sZ1EBtMZWHn32lO")
            # 实例化要请求产品(以tmt为例)的client对象
            client = tmt_client.TmtClient(cred, "ap-guangzhou")
            # 实例化一个请求对象
            req = models.TextTranslateRequest()
            # 调用接口，传入请求对象
            params = '{"SourceText":"' + text + '","Source":"auto","Target":"zh","ProjectId":0}'
            # my_json_string = json.dumps(params)
            # json_str = json.loads(my_json_string, strict=False)
            req.from_json_string(params)

            resp = client.TextTranslate(req)
            # 输出json格式的字符串回包
            return resp.TargetText

        except TencentCloudSDKException as err:
            print(err)

    def on_translator(self):
        self.isTranslator = True
        self.timer.start(1000)

    def off_translator(self):
        self.isTranslator = False
        self.timer.stop()

    def load_settings(self):
        self.settings = QSettings('my_settings.ini', QSettings.IniFormat)

        # 加载词典窗口位置
        QueryMainWindow.win_x = self.settings.value('query_win_x', 0, type=int)
        QueryMainWindow.win_y = self.settings.value('query_win_y', 0, type=int)

        # 加载窗口的宽高和位置
        window_width = self.settings.value('window_width', 657, type=int)
        window_height = self.settings.value('window_height', 745, type=int)
        window_x = self.settings.value('window_x', 0, type=int)
        window_y = self.settings.value('window_y', 0, type=int)
        self.resize(window_width, window_height)
        self.move(window_x, window_y)
        # 加载保存的设置值，如果不存在则使用默认值0

        self.value_f = self.settings.value('spin_box_value_f', 0, type=int)
        MyWindow.value_f = self.value_f
        self.value_b = self.settings.value('spin_box_value_b', 0, type=int)
        MyWindow.value_b = self.value_b

        if self.spinbox_ins_f is not None:
            self.spinbox_ins_f.setValue(self.value_f)
            self.spinbox_ins_b.setValue(self.value_b)

        # 翻译器加载设置
        self.isTranslator = self.settings.value('isTranslator', False, type=bool)
        if self.isTranslator:
            if self.auto_translator_on is not None:
                self.auto_translator_on.setChecked(True)
        else:
            self.auto_translator_off.setChecked(True)

    def save_settings(self):

        # 保持词典窗口位置
        self.settings.setValue('query_win_x', QueryMainWindow.win_x)
        print(QueryMainWindow.win_x)
        self.settings.setValue('query_win_y', QueryMainWindow.win_y)


        # 保存窗口大小
        if self.items.isHidden():
            self.settings.setValue('window_width', self.size().width())
        else:
            self.settings.setValue('window_width', self.size().width() - 177)

        self.settings.setValue('window_height', self.size().height())
        self.settings.setValue('window_x', self.pos().x())
        self.settings.setValue('window_y', self.pos().y())
        # 保存QSpinBox的值到配置文件
        if self.spinbox_ins_f is not None:
            self.settings.setValue('spin_box_value_f', self.value_f)
            self.settings.setValue('spin_box_value_b', self.value_b)

        self.settings.setValue('isTranslator', self.isTranslator)

    def closeEvent(self, event):
        # 在窗口关闭时保存设置
        self.save_settings()
        event.accept()


class VideoContainer(QWidget):
    video_processor = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_length = 0
        VideoContainer.video_processor = QRect(0, 0, 0, 0)
        # self.anc = QRect(0, 0, int(MyWindow.winsize_x-20), 50)
        self.resize(MyWindow.win_size_x, 50)
        # print(self.anc)
        print(self.size())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # painter.fillRect(self.rect(), QColor(255, 0, 0))
        # 设置边框颜色和线宽
        border_color = QColor(0, 0, 255)  # 蓝色边框
        border_width = 1  # 边框线宽度

        # 创建QPen对象并设置边框颜色和线宽
        pen = QPen(border_color, border_width)

        # 使用QPen绘制边框
        painter.setPen(pen)
        painter.drawRect(5, 5, self.width() - 10, self.height() - 10)
        painter.fillRect(VideoContainer.video_processor, QColor(112, 92, 123))

        # 设置文本颜色和字体
        text_color = QColor(255, 255, 255)  # 白色文本
        text_font = QFont("Arial", 7)  # 字体和字号

        # 创建QBrush对象并设置文本颜色
        text_brush = QBrush(text_color)

        # 使用QBrush绘制文本
        painter.setBrush(text_brush)
        painter.setFont(text_font)

        # 计算文本区域的位置以使其在 self.anc 内居中
        text_width = 399  # 假设文本的宽度为 300
        text_height = 20  # 假设文本的高度为 20
        x = self.rect().center().x() - text_width / 2
        y = self.rect().center().y() - text_height / 2

        # 创建文本区域的 QRect
        text_rect = QRect(int(x), int(y), text_width, text_height)
        if MyWindow.media_player is not None:
            video_length = MyWindow.media_player.duration()
            video_time_prosser = MyWindow.media_player.position()
            painter.drawText(text_rect, Qt.AlignCenter,
                             f"{self.format_time(video_time_prosser / 1000)} / {self.format_time(video_length / 1000)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:

            # 长方形的长度，不是组件长度
            ws = self.width() - 14
            # 获取鼠标点击的 x 坐标
            if MyWindow.media_player is not None:
                self.video_length = MyWindow.media_player.duration()
            x = event.x()
            print(x)
            # 限制进度条的长度在0到600之间
            if x < 7:
                x = 7
            elif x > ws + 7:
                x = ws + 7

            # 计算点击位置的百分比进度
            VideoContainer.video_processor = QRect(7, 7, x - 7, 39)  # 因为长方形和画图对象的大小相差了7个像素
            current_time = int((x - 7) / ws * self.video_length)
            self.update()
            if MyWindow.media_player is not None:
                MyWindow.media_player.setPosition(current_time)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"


class MyGraphicsView(QGraphicsView):
    selected_phrase = ""

    def __init__(self, scene, parent):
        super().__init__(scene)
        self.selected_text = None
        self.comparate_word_list = None
        self.word_win = None
        self.word_audio = None
        self.sentence = None
        self.word_index = None
        self.word_definite = None
        self.video_read_path = None
        self.word_definite_list = None
        self.word_definite_list_result = []
        self.is_passed_text_rect = False
        self.text_item1 = None
        self.SubWindow = None
        self.parent = parent  # 保存父窗口引用
        self.queryWindow = None
        self.text_item = None
        self.selected_phrase = []
        self.viewport().installEventFilter(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hideText)
        self.timer.setSingleShot(True)
        self.media_player = QMediaPlayer(self)
        self.undisplayed = True

    def contextMenuEvent(self, event):
        # 获取点击位置的场景坐标
        scene_pos = self.mapToScene(event.pos())
        # 获取场景中的所有图形项
        items = self.scene().items(scene_pos)

        # 检查是否有 QGraphicsTextItem
        for item in items:
            if isinstance(item, QGraphicsTextItem):
                self.text_item = item
                break

        if self.text_item:
            menu = QMenu(self)

            # 添加您的自定义菜单项
            custom_action = QAction("查词", self)
            custom_action.triggered.connect(self.handleCustomAction)
            menu.addAction(custom_action)
            custom_action = QAction("手动添加", self)
            custom_action.triggered.connect(self.manualAddText)
            menu.addAction(custom_action)
            custom_action = QAction("沙拉查词", self)
            custom_action.triggered.connect(self.open_sala)
            menu.addAction(custom_action)
            custom_action = QAction("必应搜词", self)
            custom_action.triggered.connect(self.open_web)
            menu.addAction(custom_action)

            # 调用默认的上下文菜单事件处理程序
            menu.exec_(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def open_web(self):
        # 获取文本光标
        cursor = self.text_item.textCursor()
        # 判断是否有选择的文本
        if cursor.hasSelection():
            self.selected_text = cursor.selectedText()
            webbrowser.open("https://cn.bing.com/search?q=" + self.selected_text)

    def open_sala(self):
        # 获取文本光标
        cursor = self.text_item.textCursor()
        # 判断是否有选择的文本
        if cursor.hasSelection():
            self.selected_text = cursor.selectedText()
            # 将选定文本复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(self.selected_text)
        # 模拟按下Alt键
        pyautogui.keyDown('alt')

        # 模拟按下L键
        pyautogui.press('l')

        # 松开Alt键
        pyautogui.keyUp('alt')

    def manualAddText(self):
        # 在此处添加手动添加文本的逻辑
        # 窗口布局，单词和释义及确定按钮，其他条目自动添加
        self.SubWindow = SubWindow()
        self.SubWindow.show()

    def handleCustomAction(self):
        global selected_text
        text_cursor = self.text_item.textCursor()

        if text_cursor.hasSelection():
            # 如果有选中的文本，获取选中的文本
            selected_text = text_cursor.selectedText()
            if MyGraphicsView.selected_phrase != "":
                self.queryWindow = QueryMainWindow(MyGraphicsView.selected_phrase)
                if self.queryWindow.html is None:
                    self.queryWindow.close()
                else:
                    self.queryWindow.show()
                    selected_text = MyGraphicsView.selected_phrase
                    MyGraphicsView.selected_phrase = ""
            else:
                self.queryWindow = QueryMainWindow(selected_text)
                if self.queryWindow.html is None:
                    self.queryWindow.close()
                else:
                    self.queryWindow.show()

    def mouseMoveEvent(self, event):

        # 获取鼠标在视图中的位置
        mouse_pos = self.mapToScene(event.pos())
        # 获取 proxy_button
        proxy_button = self.parent.proxy_button

        # 判断鼠标位置是否在 proxy_button 上
        if proxy_button.geometry().contains(mouse_pos.x(), mouse_pos.y()):
            # 在这里可以操作 proxy_button
            proxy_button.show()
        else:
            proxy_button.hide()  # 恢复按钮文本

        if not self.text_item.hasFocus():
            item_pos = self.text_item.mapFromScene(mouse_pos)

            text_item_rect = self.text_item.boundingRect()

            text_item_rect_x = text_item_rect.x()
            text_item_rect_height = text_item_rect.height()
            # 减少高度
            new_height = text_item_rect.height() - 16  # 请替换为您想要减少的高度值
            text_item_rect = QRectF(text_item_rect.left(), text_item_rect.top(), text_item_rect.width(), new_height)

            if text_item_rect.contains(item_pos):
                if self.parent.current_sub is not None:

                    # 使用正则表达式匹配<font>标签中的文本内容
                    matches = re.findall(r'<font[^>]*>(.*?)</font>', self.parent.current_sub.text)
                    word = ""

                    if matches:
                        for match in matches:
                            word += match.rstrip(',.?!"\'') + " "
                        word = word.rstrip(" ")
                        self.is_passed_text_rect = True
                        self.word_definite_list = []
                        with open("markWordList.csv", "r", newline="", encoding="utf-8") as csvfile:
                            csvreader = csv.reader(csvfile)
                            for row in csvreader:
                                if word.lower() == row[1].lower():
                                    self.word_index = row[0]

                                    self.sentence = row[2]
                                    self.word_definite = row[3]

                                    self.word_audio = row[4]
                                    self.video_read_path = row[5]

                                    self.word_definite_list.append(self.word_index)
                                    self.word_definite_list.append(self.sentence)
                                    self.word_definite_list.append(self.word_definite)
                                    self.word_definite_list.append(self.word_audio)
                                    self.word_definite_list.append(self.video_read_path)
                                    self.word_definite_list_result.append(self.word_definite_list.copy())
                                    self.word_definite_list.clear()

                        # 使用正则表达式匹配中文字符
                        # 使用Beautiful Soup解析HTML
                        print("_____________")
                        print(self.word_definite_list_result)
                        print("_____________")
                        for num, word_definite in enumerate(self.word_definite_list_result):
                            print(word_definite)
                            soup = BeautifulSoup(word_definite[2], 'html.parser')
                            plain_text = soup.get_text()
                            matches = re.findall(r'[\u4e00-\u9fa5（）…、，。；]+[^\u4e00-\u9fa5]*', plain_text)

                            if matches:
                                chinese_text = re.findall(r'[\u4e00-\u9fa5（）…、，。；]', matches[0])
                                word_definite.append(''.join(chinese_text))

                        word_definite_list1 = []
                        for num, word_definite in enumerate(self.word_definite_list_result):
                            word_definite_list1.append(word_definite[5])

                        word_definite_p = '<p>'.join(word_definite_list1)
                        text = "<span>" + word + "</span>" + "<p>" + word_definite_p
                        # text = '''<span>please</span><p>请（用于礼貌地请求）</p><p>请千万，请务必（用于加强请求的语气）</p>'''
                        print(text)
                        if self.undisplayed:
                            if self.word_definite_list_result:
                                local_audio_file = self.word_definite_list_result[0][
                                    3]  # Replace with your local audio file path
                                media_content = QMediaContent(QUrl.fromLocalFile("media\\" + local_audio_file))

                                self.media_player.setMedia(media_content)
                                self.media_player.play()
                                self.undisplayed = False

                        self.comparate_word_list = self.word_definite_list_result.copy()
                        self.word_definite_list_result.clear()

                        # 设置默认样式表
                        style_sheet = """
                            span { 
                                color: yellow;
                                font-size: 15px;
                                text-align: left;
                                background-color: black;
                                
                            }
                            p {
                                color: red;
                                font-size: 16px;
                                background-color: orange;
                                
                                
                                font-family:宋体;
                                margin: 2px; /* 去除默认的边距 */
                                padding: 5px; /* 添加一些内边距 */
                               
                            }
                            
                        """
                        # 创建一个QTextDocument对象
                        doc = QTextDocument()
                        # 设置文档的文本内容
                        doc.setDefaultStyleSheet(style_sheet)
                        doc.setHtml(text)
                        # 将文档设置为QGraphicsTextItem的文档
                        self.parent.words_text_item.setDocument(doc)

                        self.parent.words_text_item.show()
                        self.parent.words_text_item.setPos(mouse_pos.x() - 40,
                                                           self.size().height() - self.parent.words_text_item.boundingRect().height() - text_item_rect_height)

            else:
                self.undisplayed = True
                if self.is_passed_text_rect:
                    if self.timer is not None:
                        self.timer.start(500)  # 延迟1秒隐藏文本项
                    self.is_passed_text_rect = False

                    # 获取鼠标在视图中的位置
                    mouse_pos = self.mapToScene(event.pos())
                    item_pos2 = self.parent.words_text_item.mapFromScene(mouse_pos)
                    words_rect = self.parent.words_text_item.boundingRect()
                    if words_rect.contains(item_pos2.x(), item_pos2.y()):
                        print("进来了")

                        self.timer.stop()
                        self.parent.words_text_item.show()
                        self.is_passed_text_rect = True
                    else:
                        if self.is_passed_text_rect:
                            self.timer.start(1000)  # 延迟1秒隐藏文本项
                            self.is_passed_text_rect = False

        super().mouseMoveEvent(event)

    def hideText(self):
        # 计时器超时后隐藏文本项
        self.timer.stop()
        self.parent.words_text_item.hide()

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            # 将场景坐标转换为图形项坐标
            item_pos = self.parent.words_text_item.mapFromScene(scene_pos)
            words_rect = self.parent.words_text_item.boundingRect()
            text_item_rect = self.text_item.boundingRect()

            if self.parent.words_text_item.isVisible():

                if words_rect.contains(item_pos.x(), item_pos.y()):
                    print("进来了a")

                    # 获取当前鼠标位置所在的段落
                    text_cursor = self.parent.words_text_item.textCursor()
                    # 获取文本项的文档
                    text_doc = self.parent.words_text_item.document()
                    # 获取文档布局
                    doc_layout = text_doc.documentLayout()
                    # 将鼠标位置转换为文本坐标

                    avc = doc_layout.hitTest(item_pos, Qt.FuzzyHit)
                    # 获取文本光标的位置
                    text_cursor.setPosition(avc)

                    block_number = text_cursor.blockNumber()
                    block = self.parent.words_text_item.document().findBlockByNumber(block_number)
                    paragraph_text = block.text()
                    print(paragraph_text)
                    for text in self.comparate_word_list:
                        if paragraph_text == text[5]:
                            self.word_win = CustomMainWindow(text[1], text[2], text[4])
                            self.word_win.show()

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # 检查双击事件位置是否在文本项内
        text_item_rect = self.text_item.boundingRect()
        scene_pos = self.mapToScene(event.pos())
        item_pos = self.text_item.mapFromScene(scene_pos)
        if text_item_rect.contains(item_pos):
            # 如果在文本项内，不执行暂停/播放操作
            super().mouseDoubleClickEvent(event)
            return
        if MyWindow.media_player is not None:
            if MyWindow.media_player.state() == QMediaPlayer.PlayingState:
                MyWindow.media_player.pause()
                MyWindow.play_button.setText('播放')
            else:
                MyWindow.media_player.play()
                MyWindow.play_button.setText('暂停')

        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            # 启动定时器

            self.timer.setInterval(100)  # 设置间隔为100毫秒
            self.timer.timeout.connect(self.checkSelection)  # 连接超时信号和槽函数
            self.timer.start()  # 开始计时
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            # 停止定时器
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()  # 停止计时
                self.timer.deleteLater()  # 删除定时器对象
            MyGraphicsView.selected_phrase = ' '.join(self.selected_phrase)
            # 使用pyperclip将文本复制到剪贴板
            pyperclip.copy(MyGraphicsView.selected_phrase)
            self.selected_phrase.clear()
        super().keyReleaseEvent(event)

    def checkSelection(self):
        # 获取文本光标
        cursor = self.text_item.textCursor()
        # 判断是否有选择的文本
        if cursor.hasSelection():
            # 执行相应的操作，例如打印选择的文本

            format = QTextCharFormat()
            format.setBackground(QColor(0, 120, 215))
            cursor.setCharFormat(format)
            selected_text = cursor.selectedText()
            if self.selected_phrase:

                if selected_text == self.selected_phrase[-1]:
                    pass
                else:
                    self.selected_phrase.append(selected_text)
            else:
                self.selected_phrase.append(selected_text)

    def createScene(self):
        scene_rect = QRectF(0, 0, self.viewport().width(), self.viewport().height())
        self.setScene(QGraphicsScene(scene_rect))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            scene_rect = QRectF(0, 0, self.viewport().width(), self.viewport().height())
            self.scene().setSceneRect(scene_rect)

        return super().eventFilter(obj, event)


class SubWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.word_input = None
        self.meaning_text = None
        self.value_f = MyWindow.value_f
        self.value_b = MyWindow.value_b
        self.initUI()

    def initUI(self):
        self.setWindowTitle("添加单词和释义")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # 创建单词输入栏
        word_label = QLabel("单词:")
        self.word_input = QLineEdit()
        layout.addWidget(word_label)
        layout.addWidget(self.word_input)

        # 创建释义文本域
        meaning_label = QLabel("释义:")
        self.meaning_text = QTextEdit()
        layout.addWidget(meaning_label)
        layout.addWidget(self.meaning_text)

        # 创建确定按钮并连接槽函数
        add_button = QPushButton("确定")
        add_button.clicked.connect(self.addWordAndMeaning)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def addWordAndMeaning(self):
        # 获取单词和释义输入的文本
        word = self.word_input.text()
        meaning = self.meaning_text.toPlainText()

        # 检查单词和释义是否为空
        if word.strip() == "" or meaning.strip() == "":
            print("单词和释义不能为空")
        else:
            self.mark_word(word, meaning)
            # 清空输入框
            self.word_input.clear()
            self.meaning_text.clear()

    def mark_word(self, word, meaning):
        global partSubAtCurrent
        current_time1 = MyWindow.media_player.position()
        # 提取时间在timestamp处的字幕文本
        partSubAtCurrent = MyWindow.open_subs.at({'milliseconds': current_time1})
        new_string = word
        word_definite = new_string
        sentence = partSubAtCurrent.text
        filename = "markWordList.csv"

        # 读取现有的最大索引（如果文件存在）
        try:
            with open(filename, "r", newline="", encoding="utf-8") as csvfile:
                csvreader = csv.reader(csvfile)
                max_index = max(int(row[0]) for row in csvreader)
        except FileNotFoundError:
            max_index = 0
        except ValueError:
            print("读取生词表失败，因为文件为空，删除markWordList.csv文件后重试")

        # 写入新的条目，并自动加上索引

        # 写入列表数据
        start_time = partSubAtCurrent[0].start
        end_time = partSubAtCurrent[0].end
        start_time = str(start_time)
        end_time = str(end_time)
        start_time = self.srt_to_seconds(start_time)
        end_time = self.srt_to_seconds(end_time)
        # 创建一个视频媒体对象，并指定视频文件的路径
        mediaclip = VideoFileClip(video_name)

        # 截取视频中的一段，从第10秒到第20秒
        clip = mediaclip.subclip(start_time - self.value_f / 1000, end_time + self.value_b / 1000)
        # 保存输出文件，并指定输出文件的路径和名称

        # 获取当前脚本所在的目录
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # 创建子文件夹名称，固定为"media"
        subfolder_name = "media"

        # 构建子文件夹路径
        subfolder_path = os.path.join(script_directory, subfolder_name)

        # 如果子文件夹不存在，则创建它
        if not os.path.exists(subfolder_path):
            os.mkdir(subfolder_path)

        # 获取当前时间并格式化为字符串
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # 构建视频文件名，以当前时间命名
        video_filename = f"{current_time}.mp4"

        # 构建输出视频文件的完整路径
        video_filepath = os.path.join(subfolder_path, video_filename)

        # 进行其他操作，如写入视频文件
        clip.write_videofile(video_filepath)

        # 复制音频文件到media文件夹
        # 定义原始音频文件路径和目标子文件夹路径
        original_audio_file = audio_path_abc

        target_subfolder = "media\\"

        # 确保目标子文件夹存在
        if not os.path.exists(target_subfolder):
            os.makedirs(target_subfolder)

        # 构建目标音频文件的完整路径
        if audio_path_abc != "":
            target_audio_file = os.path.join(target_subfolder, os.path.basename(original_audio_file))

            if not os.path.exists(target_audio_file):
                # 执行文件复制操作
                shutil.copy(original_audio_file, target_audio_file)

                print(f"音频文件已拷贝到{target_audio_file}")
            else:
                print("音频文件已经存在")

        new_word = word
        new_sentence = sentence
        word_definite = meaning
        new_index = max_index + 1
        new_audio_path = " "
        video_path = video_filename
        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([new_index, new_word, new_sentence, word_definite, new_audio_path, video_path])

    def srt_to_seconds(self, srt_time):
        # 使用正则表达式匹配时分秒毫秒
        match = re.match(r"(\d+):(\d+):(\d+),(\d+)", srt_time)
        if match:
            # 将匹配到的字符串转换为整数
            hours, minutes, seconds, milliseconds = map(int, match.groups())
            # 计算总的秒数
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            # 返回结果
            return total_seconds
        else:
            # 如果没有匹配到，返回 None
            return None


class QueryMainWindow(QDialog):
    win_x = 0
    win_y = 0

    def __init__(self, query_word):
        super().__init__()
        self.audio_fileName = None
        self.media_player = None
        self.web_view = None
        self.move(QueryMainWindow.win_x, QueryMainWindow.win_y)
        self.query_word = query_word
        self.html = self.query_word_toHtml()
        self.worker = None
        if self.html is not None:
            self.initUI()

    def initUI(self):
        global audio_path_abc
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # 设置本地HTML文件的路径
        replacement_block = '<input type="radio" name="options" value="option3"> <div class="sblock_labels">'
        replacement_b = '<input type="radio" name="options" value="option3"> <div class="sense"> <strong class="sn_letter">b&nbsp;</strong>'
        replacement_uro = '<input type="radio" name="options" value="option3"> <div class="uro_line">'
        pattern_b = r'<div class="sense"> <strong class="sn_letter">b&nbsp;</strong>'
        pattern_block = r'<div class="sblock_labels">'
        pattern_uro = r'<div class="uro_line">'

        html1 = re.sub(pattern_block, replacement_block, self.html)
        html2 = re.sub(pattern_b, replacement_b, html1)
        if '"ure"' in self.html:
            html2 = re.sub(pattern_uro, replacement_uro, html2)
        # 给html加div标签，一遍提取释义
        text = html2
        pattern = r'<input type="radio" name="options" value="option3">'
        replacement_list = ['<div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">',
                            '</div><div><input type="radio" name="options" value="option3">']

        def replace_function(match):
            global audio_fileName
            try:
                return replacement_list.pop(0)
            except IndexError:
                # 处理列表为空的情况
                return "单词释义过多，所有不显示 --！"  # 或者你想要的默认替换值

        new_text = re.sub(pattern, replace_function, text)
        new_text = new_text + "</div>"

        pattern = r'(sound://[^"]+\.mp3)'
        match = re.search(pattern, new_text)

        if match:
            file_name = match.group(1)  # 获取捕获的文件名部分
            audio_fileName = file_name.replace("sound://", "").replace("/", "")  # 使用捕获的文件名部分创建新字符串
            audio_path_abc = "abc/" + audio_fileName
            audio_path = audio_path_abc
        else:
            audio_fileName = ""
            print("没有找到单词发音")

        pattern_sound = r'sound://[^"]+\.mp3'
        new_text = re.sub(pattern_sound, audio_path_abc, new_text)
        html_file_path = cssfile + new_text
        play_button1 = QPushButton("Play Audio")
        layout.addWidget(play_button1)
        self.media_player = QMediaPlayer(self)
        play_button1.clicked.connect(self.play_local_audio)
        # 加载本地HTML文件
        self.setLayout(layout)

        # 响应console返回html字符串
        class WebEnginePage(QWebEnginePage):

            def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
                self.mark_word(message)

            def mark_word(self, word_definite):
                global partSubAtCurrent
                current_time1 = MyWindow.media_player.position()
                # 提取时间在timestamp处的字幕文本
                partSubAtCurrent = MyWindow.open_subs.at({'milliseconds': current_time1})
                # 打印字幕文本
                sentence = partSubAtCurrent.text
                # 去除释义的单选框
                unwanted_text = '''<input type="radio" name="options" value="option3">'''
                new_string = word_definite.replace(unwanted_text, "")
                word_definite = new_string
                sentence = partSubAtCurrent.text
                filename = "markWordList.csv"

                # 读取现有的最大索引（如果文件存在）
                try:
                    with open(filename, "r", newline="", encoding="utf-8") as csvfile:
                        csvreader = csv.reader(csvfile)
                        max_index = max(int(row[0]) for row in csvreader)
                except FileNotFoundError:
                    max_index = 0
                except ValueError:
                    print("读取生词表失败，因为文件为空，删除markWordList.csv文件后重试")

                # 写入新的条目，并自动加上索引

                # 写入列表数据
                start_time = partSubAtCurrent[0].start
                end_time = partSubAtCurrent[0].end
                start_time = str(start_time)
                end_time = str(end_time)
                start_time = self.srt_to_seconds(start_time)
                end_time = self.srt_to_seconds(end_time)
                # 创建一个视频媒体对象，并指定视频文件的路径
                mediaclip = VideoFileClip(video_name)

                # 截取视频中的一段，从第10秒到第20秒
                clip = mediaclip.subclip(start_time - value_f, end_time + value_b)
                # 保存输出文件，并指定输出文件的路径和名称

                # 获取当前脚本所在的目录
                script_directory = os.path.dirname(os.path.abspath(__file__))

                # 创建子文件夹名称，固定为"media"
                subfolder_name = "media"

                # 构建子文件夹路径
                subfolder_path = os.path.join(script_directory, subfolder_name)

                # 如果子文件夹不存在，则创建它
                if not os.path.exists(subfolder_path):
                    os.mkdir(subfolder_path)

                # 获取当前时间并格式化为字符串
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                # 构建视频文件名，以当前时间命名
                video_filename = f"{current_time}.mp4"

                # 构建输出视频文件的完整路径
                video_filepath = os.path.join(subfolder_path, video_filename)

                # 进行其他操作，如写入视频文件
                clip.write_videofile(video_filepath)

                # 复制音频文件到media文件夹
                # 定义原始音频文件路径和目标子文件夹路径
                original_audio_file = audio_path_abc

                target_subfolder = "media\\"

                # 确保目标子文件夹存在
                if not os.path.exists(target_subfolder):
                    os.makedirs(target_subfolder)

                # 构建目标音频文件的完整路径

                if audio_path_abc != "":
                    target_audio_file = os.path.join(target_subfolder, os.path.basename(original_audio_file))

                    # 执行文件复制操作
                    if not os.path.exists(target_audio_file):
                        shutil.copy(original_audio_file, target_audio_file)

                    print(f"音频文件已拷贝到{target_audio_file}")

                new_word = selected_text
                new_sentence = sentence
                word_definite = word_definite.strip()
                new_index = max_index + 1
                new_audio_path = audio_fileName
                video_path = video_filename
                with open(filename, "a", newline="", encoding="utf-8") as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow([new_index, new_word, new_sentence, word_definite, new_audio_path, video_path])

            def srt_to_seconds(self, srt_time):
                # 使用正则表达式匹配时分秒毫秒
                match = re.match(r"(\d+):(\d+):(\d+),(\d+)", srt_time)
                if match:
                    # 将匹配到的字符串转换为整数
                    hours, minutes, seconds, milliseconds = map(int, match.groups())
                    # 计算总的秒数
                    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
                    # 返回结果
                    return total_seconds
                else:
                    # 如果没有匹配到，返回 None
                    return None

        self.web_view.setPage(WebEnginePage(self.web_view))
        self.web_view.setHtml(html_file_path)

    def play_local_audio(self):
        local_audio_file = audio_path_abc  # Replace with your local audio file path
        media_content = QMediaContent(QUrl.fromLocalFile(local_audio_file))
        self.media_player.setMedia(media_content)
        self.media_player.play()

    def query_word_toHtml(self):
        wordIndex = None
        try:
            wordIndex = headwords.index(self.query_word.encode())
        except:
            print(f"没有找到:{self.query_word}")
        if wordIndex is not None:
            word, html = items[wordIndex]
            word, html = word.decode(), html.decode()
            if html.startswith("@"):
                word2 = html.split('=')
                word = word2[1].strip()
                wordIndex = headwords.index(word.encode())
                word, html = items[wordIndex]
                word, html = word.decode(), html.decode()
            print(f"Found match: {word}")
            return html
        else:
            return None  # 如果未找到匹配的单词，则返回None

    # def resizeEvent(self, Event):
    #     QueryMainWindow.win_x = self.pos().x()
    #     print(QueryMainWindow.win_x)
    #     QueryMainWindow.win_y = self.pos().y()
    #     super().resizeEvent(Event)

    def moveEvent(self, event):
        QueryMainWindow.win_x = self.pos().x()

        QueryMainWindow.win_y = self.pos().y()
        super().moveEvent(event)

class TimeShiftDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('时间调整')

        # 创建 QSpinBox 控件用于输入秒数
        self.seconds_spinbox = QSpinBox(self)
        self.seconds_spinbox.setMinimum(-9999)  # 设置最小值为较小的负数
        self.seconds_spinbox.setMaximum(9999)  # 设置最大值为较大的正数
        self.seconds_spinbox.setValue(0)  # 设置默认值

        # 创建 QSpinBox 控件用于输入毫秒数
        self.milliseconds_spinbox = QSpinBox(self)
        self.milliseconds_spinbox.setMinimum(-999)  # 设置最小值为较小的负数
        self.milliseconds_spinbox.setMaximum(999)  # 设置最大值为较大的正数
        self.milliseconds_spinbox.setValue(0)  # 设置默认值

        # 创建标签用于显示 "秒数" 和 "毫秒数"
        seconds_label = QLabel('秒数:', self)
        milliseconds_label = QLabel('毫秒数:', self)

        # 创建按钮框
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(seconds_label)
        layout.addWidget(self.seconds_spinbox)
        layout.addWidget(milliseconds_label)
        layout.addWidget(self.milliseconds_spinbox)
        layout.addWidget(button_box)
        self.setLayout(layout)


class ChipVideoDelay(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('时间调整')

        # 创建 QSpinBox 控件用于输入向前偏移（毫秒）
        self.forward_spinbox = QSpinBox(self)
        self.forward_spinbox.setRange(0, 5000)

        # 创建 QSpinBox 控件用于输入向后偏移（毫秒）
        self.backward_spinbox = QSpinBox(self)
        self.backward_spinbox.setRange(0, 5000)

        # 创建标签用于显示 "向前偏移/毫秒" 和 "向后偏移/毫秒"
        forward_label = QLabel('向前偏移/毫秒:', self)
        backward_label = QLabel('向后偏移/毫秒:', self)

        # 创建按钮框
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(forward_label)
        layout.addWidget(self.forward_spinbox)
        layout.addWidget(backward_label)
        layout.addWidget(self.backward_spinbox)
        layout.addWidget(button_box)
        self.setLayout(layout)


class CustomMainWindow(QDialog):
    def __init__(self, sentence, word_definite, word_video):
        super().__init__()
        # self.setGeometry(MyWindow.winfo_x + MyWindow.win_size_x, MyWindow.winfo_y, 300, 500)
        self.resize(270, 400)
        video_widget = QVideoWidget(self)
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        video_widget.setFixedSize(256, 144)
        layout.addWidget(video_widget)

        # Create QMediaPlayer and load local video
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(video_widget)

        # 加载视频
        script_directory = os.path.dirname(os.path.abspath(__file__))
        subfolder_path = os.path.join(script_directory, "media\\" + word_video)
        video_path = subfolder_path
        media_content = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media_content)

        self.media_player.mediaStatusChanged.connect(self.onMediaStatusChanged)

        # Add QLabel to display a sentence with a width of 40
        sentence_label = QLabel(sentence)
        sentence_label.setFixedSize(256, 44)
        sentence_label.setAlignment(Qt.AlignCenter)
        sentence_label.setWordWrap(True)
        sentence_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)  # Allow text selection

        web_engine_view = QWebEngineView(self)
        # Load HTML content
        web_engine_view.setHtml(word_definite + cssfile)

        layout.addWidget(sentence_label)
        layout.addWidget(web_engine_view)

        self.setLayout(layout)

    def play_video(self):
        # Play the video when the QTimer times out
        self.media_player.play()

    def onMediaStatusChanged(self, status):
        if status == QMediaPlayer.LoadedMedia:
            self.media_player.play()


class ExportWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.inserted_tags = None
        self.text_edit2 = None
        self.text_edit = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("字段导出设置")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        H_layout = QHBoxLayout()

        # 创建复选框和输入框
        labels = ["索引\n%index%", "单词\n%word%", "句子\n%sentence%", "释义\n%meaning%", "单词发音\n%audio%",
                  "视频\n%video%"]

        # 创建并添加标签到布局
        for label_text in labels:
            label = QLabel(label_text, self)
            H_layout.addWidget(label)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText(
            "想导出哪个字段就写入那个字段下面代表的标签.\neg:想导出单词，就输入%word%标签.\n标签的前后可以自定义内容，非常自由....")
        self.text_edit2 = QTextEdit(self)
        H_widgit = QWidget()
        H_widgit.setLayout(H_layout)
        layout.addWidget(H_widgit)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.text_edit2)

        self.text_edit.textChanged.connect(self.copyText)

        # 创建导出按钮
        export_button = QPushButton("导出", self)
        export_button.clicked.connect(self.exportFields)
        layout.addWidget(export_button)

        self.setLayout(layout)

        self.inserted_tags = set()

    def copyText(self):
        self.text_edit2.clear()
        # 获取 self.text_edit 中的文本
        text = self.text_edit.toPlainText()

        if os.path.exists('markWordList.csv'):
            with open("markWordList.csv", "r", newline="", encoding="utf-8") as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    text1 = text.replace('%index%', row[0]).replace('%word%', row[1]).replace('%sentence%', row[2]). \
                        replace('%meaning%', row[3]).replace('%audio%', row[4]).replace('%video%', row[5])
                    self.text_edit2.append(text1)
            # 创建一个集合来跟踪已添加的标记

    def exportFields(self):
        # 获取文本域的内容
        text_content = self.text_edit2.toPlainText()

        if not text_content:
            return  # 如果文本域内容为空，则不保存

        # 打开文件对话框，让用户选择保存的文件路径
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "保存为txt文件", "", "Text Files (*.txt)")

        if file_path:
            # 用户选择了文件路径，将文本内容写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_content)


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
