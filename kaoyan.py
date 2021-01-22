#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
import numpy as np




# In[9]:


df_info = pd.read_csv('大学信息_整理后.csv',encoding='utf-8')
df_info.head()


# In[15]:


def transform_attr(x):
    #转换学校属性
    if '211' in x and '985' not in x:
        return 211 
    elif '985' in x:
        return '985'
    else:
        return '双非'
    
def transform_type(x):
    #转换学校类型
    if '理工类' in x or '理工类院校' in x or '理工科' in x or '理工、教学研究型大学' in x or '理工类\n[4]' in x or '理工\n[6]' in x:
        return '理工'
    elif '综合类' in x or '综合性大学\n[3]' in x or '综合类（应用型大学）' in x or '综合、研究教学型大学' in x or '综合类大学' in x or '综合师范类' in x:
        return '综合'
    elif '师范类院校' in x or '师范类' in x or '师范类（综合类）' in x or '师范（综合）' in x or '地方师范院校' in x:
        return '师范'
    elif '农林类' in x or '农业类' in x: 
        return '农林'
    elif '医药类' in x:
        return '医药'
    elif '民族类' in x:
        return '民族'
    elif '未知' in x or '国有企业' in x or '科技型企业' in x or '公立大学' in x:
        return '其他'
    else:
        return x 
    


# In[ ]:





# In[19]:


# 筛选字段
df_info= df_info[['school','province','school_level','school_types']]


# In[20]:


# 处理省份数据
df_info.loc[(df_info.school=='北京工商大学')&(df_info.province=='未知'), 'province']= '北京' 
df_info.loc[(df_info.school=='哈尔滨工程大学')&(df_info.province=='未知'), 'province']= '哈尔滨' 
df_info.loc[(df_info.school=='江苏大学')&(df_info.province=='未知'), 'province']= '江苏' 
df_info.loc[(df_info.school=='青岛大学')&(df_info.province=='未知'), 'province']= '山东' 
df_info.loc[(df_info.school=='北京石油化工学院')&(df_info.province=='未知'), 'province']= '北京' 
df_info.loc[(df_info.school=='齐鲁工业大学')&(df_info.province=='未知'), 'province']= '山东'
df_info.loc[(df_info.school=='江苏科技大学')&(df_info.province=='未知'), 'province']= '江苏'
df_info.loc[(df_info.school=='浙江农林大学')&(df_info.province=='未知'), 'province']= '浙江'
df_info.loc[(df_info.school=='燕山大学')&(df_info.province=='未知'), 'province']= '河北'
df_info.loc[(df_info.school=='福州大学')&(df_info.province=='未知'), 'province']= '福建'
df_info.loc[(df_info.school=='内蒙古科技大学')&(df_info.province=='未知'), 'province']= '内蒙古'


# In[22]:


df_info.to_csv('大学信息_整理后.csv',index=False, encoding='utf-8')


# In[23]:


df_info.head()


# In[24]:


df_info = df_info.drop_duplicates()#删除重
df_info.head()


# In[25]:


df_info.shape


# In[26]:


df = pd.read_csv('考研调剂数据-3.09.csv', encoding='utf-8')
df.shape


# In[27]:


df_2020 = df[df['time'].str.contains('2020')].copy()
df_2020.shape


# In[28]:


pd.merge(df_2020,df_info,how = 'left',on = 'school').shape


# In[29]:


df_all = pd.merge(df_2020,df_info,how = 'left',on = 'school')

from IPython.display import clear_output, Image, display

display(df_all)
df_all.shape


# In[30]:


df_all = df_all[['school','name','time','province','school_level','school_types']]
df_all.head()


# In[31]:


# 查看缺失数据
df_all.isnull().sum()


# In[32]:


# 发布时间对应的发布频次
pub_time = df_all.time.value_counts().sort_index()
pub_time


# In[37]:


import pyecharts
from pyecharts.charts import Line 
from pyecharts import options as opts 


# In[38]:


#调剂信息发布时间走势图
line1 = Line(init_opts=opts.InitOpts(width='1280px',height='600px'))
line1.add_xaxis(pub_time.index.tolist())
line1.add_yaxis('发布热度',pub_time.values.tolist(),
               areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
               label_opts=opts.LabelOpts(is_show=True))
line1.set_global_opts(title_opts=opts.TitleOpts(title='调剂信息发布时间走势图'),
                     toolbox_opts=opts.ToolboxOpts(),
                     visualmap_opts=opts.VisualMapOpts())
line1.render_notebook()


# In[39]:


#学校层次
level_perc = df_all.school_level.value_counts() / df_all.school_level.value_counts().sum()
display(level_perc)
level_perc = np.round(level_perc * 100 ,2)
level_perc


# In[40]:


from pyecharts.charts import Pie 
from pyecharts.globals import ThemeType


# In[42]:


#绘制饼图
pie1 = Pie(init_opts=opts.InitOpts(width='500px',height='600px'))
pie1.add("", 
         [*zip(level_perc.index, level_perc.values)], 
         radius=["40%","75%"]) 
pie1.set_global_opts(title_opts=opts.TitleOpts(title='学校层次分布'), 
                     legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
                     toolbox_opts=opts.ToolboxOpts())   
pie1.set_series_opts(label_opts=opts.LabelOpts(formatter="{c}%")) 
pie1.render_notebook()


# In[43]:


#学校类型
type_perc = df_all.school_types.value_counts() / df_all.school_types.value_counts().sum()
type_perc = np.round(type_perc*100,2) 


# In[44]:


pie2 = Pie(init_opts=opts.InitOpts(theme=ThemeType.WONDERLAND, width='1280px', height='650px')) 
pie2.add("", 
         [*zip(type_perc.index, type_perc.values)], 
         radius=["40%","75%"]) 
pie2.set_global_opts(title_opts=opts.TitleOpts(title='学校类型分布'), 
                     legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
                     toolbox_opts=opts.ToolboxOpts())   
pie2.set_series_opts(label_opts=opts.LabelOpts(formatter="{c}%")) 

pie2.render_notebook()


# In[45]:


province_num = df_all.province.value_counts().sort_values()
province_num


# In[46]:


from pyecharts.charts import Bar


# In[47]:


# 条形图
bar1 = Bar(init_opts=opts.InitOpts(width='1280px', height='1000px')) 
bar1.add_xaxis(province_num.index.tolist())
bar1.add_yaxis("省份", province_num.values.tolist()) 
bar1.set_global_opts(title_opts=opts.TitleOpts(title="调剂信息发布数省份分布"), 
                     toolbox_opts=opts.ToolboxOpts(),
                     visualmap_opts=opts.VisualMapOpts(max_=110)) 
bar1.set_series_opts(label_opts=opts.LabelOpts(position='right'))  # 标签
bar1.reversal_axis() 
bar1.render_notebook()


# In[48]:


from pyecharts.charts import Map


# In[49]:


c = Map(init_opts=opts.InitOpts(width='800px', height='750px'))
c.add('',[list(z) for z in zip(province_num.index.tolist(), province_num.values.tolist())], 'china')
c.set_global_opts(title_opts=opts.TitleOpts('调剂信息省份分布地图'), 
                  toolbox_opts=opts.ToolboxOpts(is_show=True), 
                  visualmap_opts=opts.VisualMapOpts(max_=110)) 
c.render_notebook()


# In[51]:


import jieba.analyse #cmd pip install jieba


# In[52]:


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
stop_words.extend(['查看','详细','详见','详情','与化','03','02','01','正文','多个','相关'])
#字段分词处理
word_num = jieba.analyse.extract_tags(txt,
                                      topK=100,
                                      withWeight=True,
                                      allowPOS=())
# 去停用词
word_num_selected = []
for i in word_num:
    if i[0] not in stop_words:
        word_num_selected.append(i)

key_words = pd.DataFrame(word_num_selected,columns = ['words','num'])
key_words.head()


# In[53]:


key_words[:50]


# In[54]:


from pyecharts.charts import WordCloud 
from pyecharts.globals import SymbolType,ThemeType 


# In[55]:


word1 = WordCloud(init_opts=opts.InitOpts(width='1280px', height='750px'))
word1.add("", [*zip(key_words.words, key_words.num)], 
         word_size_range=[20, 200], shape='diamond') 
word1.set_global_opts(title_opts=opts.TitleOpts(title="调剂专业分布"), 
                     toolbox_opts=opts.ToolboxOpts())
word1.render_notebook()


# In[56]:


from pyecharts.charts import Page

page = Page()  
page.add(line1, pie1, pie2, bar1, c, word1)
page.render_notebook()


# In[ ]:




