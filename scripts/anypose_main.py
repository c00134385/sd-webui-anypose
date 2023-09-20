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

# def LoadTagsFile():    
#     dic={}
#     loadjsonfiles(path1,dic)
#     loadjsonfiles(path2,dic)
#     return json.dumps(dic,ensure_ascii=False)                            
 
# def loadjsonfiles(path,dic):
#     files = os.listdir( path ) 
#     for item in files:
#         if item.endswith(".json"):
#             filepath=path+'/'+item
#             filename=filepath[filepath.rindex('/') + 1:-5]
#             with open(filepath, "r",encoding="utf-8-sig") as f:
#                 res=json.loads(f.read())                       
#                 dic[filename]=res

class Script(scripts.Script):
                        
    def title(self):
        return "AnyPose"
            
    def show(self, is_img2img):
        return scripts.AlwaysVisible
              
    def ui(self, is_img2img):
        print(f'------------------------------------------------ title: AnyPose')
        if(is_img2img):
            eid='anypose-prompt2'
            tid='anypose-area2'
        else:
            eid='anypose-prompt1'     
            tid='anypose-area1'           
        with gr.Row(elem_id=eid):
            with gr.Accordion(label="AnyPose Picker", open=False):
                # textarea=gr.TextArea(self.json,elem_id=tid)
                textarea1 = gr.TextArea("this is anypose body", elem_id=tid)                                                                                         
        return [textarea1]


    
       
        
                
 

