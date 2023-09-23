import modules.scripts as scripts
import gradio as gr
import os,json
import json
import random

current_script = os.path.realpath(__file__)
current_folder = os.path.dirname(current_script)   
work_basedir = os.path.dirname(current_folder)   #本插件目录  
path1 = work_basedir+ r"/json"
path2 = work_basedir+ r"/yours"
pathrandom = work_basedir+ r"/random"


def LoadAssetsFiles():
    dic={}
    loadJsonFiles(path1, dic)
    loadJsonFiles(path2, dic)
    # print(f'dic: {dic}')
    return json.dumps(dic,ensure_ascii=False)  

def loadJsonFiles(path, dic):
    files = os.listdir(path) 
    for item in files:
        if item.endswith(".json"):
            filepath=path+'/'+item
            filename=filepath[filepath.rindex('/') + 1:-5]
            with open(filepath, "r",encoding="utf-8-sig") as f:
                res=json.loads(f.read())                       
                dic[filename]=res

class Script(scripts.Script):
    json = LoadAssetsFiles()
                        
    def title(self):
        return "AnyPose"
            
    def show(self, is_img2img):
        return scripts.AlwaysVisible
              
    def ui(self, is_img2img):
        print(f'------------------------------------------------ title: AnyPose')
        if(is_img2img):
            eid='anypose-view1'
            tid='anypose-area2'
        else:
            eid='anypose-view2'     
            tid='anypose-area1'           
        with gr.Row(elem_id=eid):
            with gr.Accordion(label="AnyPose Picker", open=False):
                textarea = gr.TextArea(self.json, elem_id=tid) 
                with gr.Column(scale=4,elem_id="anypose-optit"):
                    btnreload=gr.Button('🔄',elem_classes="anypose-reload sm secondary gradio-button svelte-1ipelgc")
                    gr.Button('清空正面提示词', variant="secondary",elem_classes="anypose-clear")
                    gr.Button('清空负面提示词',variant="secondary",elem_classes="anypose-clear")
                # textarea=gr.TextArea(self.json,elem_id=tid)

        def reloadData():
            return LoadAssetsFiles()
        
        btnreload.click(fn=reloadData,inputs=None,outputs=textarea)                                                                                                  
        return [btnreload]


    
       
        
                
 

