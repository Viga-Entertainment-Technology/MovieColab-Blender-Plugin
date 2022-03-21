bl_info = {
    "name": "MovieColab",
    "author": "Sarthak Mehta",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > MovieColab",
    "description": "Blender Add On for Movie Colab",
    "warning": "",
    "doc_url": "",
    "category": "Movie Colab",
}

import requests
import json
import bpy
import bpy
import os

filepath = ""
directory = ""

MOVCOLAB_URL= 'https://movie-colab-dev-rvz2hoyrua-as.a.run.app/'
SSO_URL='https://viga-sso-stage-u44si7afja-as.a.run.app/'

valid=False

token=""
project={}# stores project info{id,name} 
Project_names=[]
project_dict={}

sequences={} # stores project->sequences{id,name,code}
sequences_names=[]
sequence_dict={}

shots={}# stores shots string
Shot_names=[]
shot_dict={}

tasks={}#stores tasks string
Task_names=[]
task_dict={}

asset={}
asset_dict={}
Asset_names=[]

name=""
asset_version={}

first_login=0

x=""

def get_token(mail, password):
    details = {
        'email': mail,
        'password': password
    }
    res = requests.post(SSO_URL+"api/token/", json=details)
    global filepath
    global directory
    global token
    global first_login
    global x
    if(res.status_code<300):
       access_token=res
       filepath = bpy.data.filepath
       directory = os.path.dirname(filepath)
       token=res.json()['access']
       first_login=1
       x=token      
       return True
    else:
       return False

def get_project():
    r=requests.get(MOVCOLAB_URL+"project/",headers={'Authorization':'Bearer '+str(x)})
    return r.json()    

def get_sequences(project_id):
    r=requests.get(MOVCOLAB_URL+"trackables/shot-sequence?project="+str(project_id),headers={'Authorization':'Bearer '+str(x)})
    return r.json() 

def get_shot(project_id,sequence_id):
    r=requests.get(MOVCOLAB_URL+"trackables/shot?project="+str(project_id)+"&parent_sequence="+str(sequence_id),headers={'Authorization':'Bearer '+x})
    return r.json()

def get_Shot_version(shot_id):
    r=requests.get(MOVCOLAB_URL+"trackables/shot-version?shot="+str(shot_id),headers={'Authorization':'Bearer '+x})
    return(r.json())

def create_shot_SS(name,shot):
    data={ 

        "name": "String", 

        "shot": 0, 
    }
    data["name"]=name
    data["shot"]=shot
    ss_directory=str(directory)+"\\"+str(name)+'.png'
    print(ss_directory)
    
    if(os.path.isfile(ss_directory)):
        
      files=[('file',(ss_directory,open(ss_directory,'rb')))]
      r=requests.post(MOVCOLAB_URL+"trackables/shot-version/",headers={'Authorization':'Bearer '+x},data=data,files=files)
      return (r.status_code)
  
    else:
        return 101
    
def create_shot_sequence(name,shot):
    data={ 

        "name": "String", 

        "shot": 0, 
    }
    data["name"]=name
    data["shot"]=shot
    ss_directory=str(directory)+"\\"+str(name)+'.mp4'
    print(ss_directory)
    if(os.path.isfile(ss_directory)):
       files=[('file',(ss_directory,open(ss_directory,'rb')))]
       r=requests.post(MOVCOLAB_URL+"trackables/shot-version/",headers={'Authorization':'Bearer '+x},data=data,files=files)
       return (r.status_code)
    else:
       return 101
      

def get_task(project_id,shot_id):
    r=requests.get(MOVCOLAB_URL+"trackables/task/?project="+str(project_id)+"&linked="+str(shot_id)+"&assigned=1",headers={'Authorization':'Bearer '+str(x)})
    return r.json()  

def render_and_save(name):
    render_name=name+'.png'
    bpy.context.scene.render.filepath = os.path.join(directory, (render_name))
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.view_show('INVOKE_DEFAULT')
    bpy.ops.render.render(animation=False,write_still=True, use_viewport=True)
    
def render_anim(name):
    render_name=name+'.mp4'
    bpy.context.scene.render.filepath = os.path.join(directory, (render_name))
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.ops.render.render(animation=True,write_still=True, use_viewport=True)
    bpy.ops.render.play_rendered_anim('INVOKE_DEFAULT')
    
def MessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
class Sequences(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_sequence"
    bl_label = "Get Sequences"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        global sequences
        global sequences_names
        sequences_names.clear()
        global sequence_dict
        sequence_dict.clear()
        
        if(mycred.Project!=""):
             sequences=get_sequences(project['results'][project_dict[mycred.Project]]['id'])
        
             for i in range(sequences['count']):
                 sequence_dict[sequences['results'][i]['code']]=i
            
             for i in range(sequences['count']):
                 sequences_names.append((sequences['results'][i]['code'],sequences['results'][i]['code'],""))
                 
        else:
             MessageBox("No projects available","Sequence")
             
        return{'FINISHED'}
    
class ProjectInfo(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_project"
    bl_label = "Get Project Info"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        global project
        global Project_names
        Project_names.clear()
        global project_dict
        project_dict.clear()
        project=get_project()
        #Create project dictionary
        if(valid): 
            for i in range(project['count']):
                project_dict[project['results'][i]['name']]=i
            
            for i in range(project['count']):
                Project_names.append((project['results'][i]['name'],project['results'][i]['name'],""))
        else:
            MessageBox("Can't access projects","Projects",'ERROR')   
        return{'FINISHED'}
                    
class Shot_list(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_shot_list"
    bl_label = "Get shots list"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        global shots
        global Shot_names
        Shot_names.clear()
        global shot_dict
        shot_dict.clear()
        
        if(mycred.Project!="" and mycred.Sequence!=""):
            shots=get_shot(project['results'][project_dict[mycred.Project]]['id'],sequences['results'][sequence_dict[mycred.Sequence]]['id'])
        
            for i in range(shots['count']):
                shot_dict[shots['results'][i]['code']]=i
            
            for i in range(shots['count']):
                Shot_names.append((shots['results'][i]['code'],shots['results'][i]['code'],""))
        
        else:
            MessageBox("No sequence available","Shot")
        return{'FINISHED'}
    
class Create_Shot(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.create_shot"
    bl_label = "Create shot"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        if(mycred.Shot!=""):
           shot=shots['results'][shot_dict[mycred.Shot]]['id']
           version=get_Shot_version(shots['results'][shot_dict[mycred.Shot]]['id'])
        
           if(version['count']!=0):
              index=version['count']-1
              version_name=version['results'][index]['name']
              shot_num=int(version_name[version_name.find('v')+2:])+1
              name_SS=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+'v'+(3-len(str(shot_num)))*"0"+str(shot_num)
       
           else:
              name_SS=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+"v001"
           
           statuscode=create_shot_SS(name_SS,shot)
        
           if(statuscode==401):
              MessageBox("Failed","Sequence Shot version upload",'ERROR')
        
           elif(statuscode==201):
              MessageBox("Success","Sequence Shot version upload")
              
           elif(statuscode==101):
              MessageBox("No such file in the directory","Sequence Shot version upload")
        else:
              MessageBox("No shots to upload","Sequence Shot version upload")
              
        return{'FINISHED'}

class Create_Shot_sequence(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.create_shot_sequence"
    bl_label = "Create shot sequence"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        if(mycred.Shot!=""):
           shot=shots['results'][shot_dict[mycred.Shot]]['id']
           version=get_Shot_version(shots['results'][shot_dict[mycred.Shot]]['id'])
        
           if(version['count']!=0):
              index=version['count']-1
              version_name=version['results'][index]['name']
              shot_num=int(version_name[version_name.find('v')+2:])+1
              name_Seq=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+'v'+(3-len(str(shot_num)))*"0"+str(shot_num)
       
           else:
              name_Seq=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+"v001"
           
           statuscode=create_shot_sequence(name_Seq,shot)
        
           if(statuscode==401):
              MessageBox("Failed","Sequence Shot version upload",'ERROR')
          
           elif(statuscode==201):
              MessageBox("Success","Sequence Shot version upload")
            
           elif(statuscode==101):
              MessageBox("No such file in the directory","Sequence Shot version upload")
           
        else:
            MessageBox("No shots to upload","Sequence Shot version upload")
        return{'FINISHED'}

class Tasks(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_tasks"
    bl_label = "Get tasks assigned"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        global tasks
        global Task_names
        Task_names.clear()
        global task_dict
        task_dict.clear()
        if(mycred.Project!="" and mycred.Shot!=""):
             tasks=get_task(project['results'][project_dict[mycred.Project]]['id'],shots['results'][shot_dict[mycred.Shot]]['id'])
        
             for i in range(tasks['count']):
                   task_dict[tasks['results'][i]['name']]=i
            
             for i in range(tasks['count']):
                   Task_names.append((tasks['results'][i]['name'],tasks['results'][i]['name'],""))
        else:
             MessageBox("No shots available","Tasks")  
              
        return{'FINISHED'}

class Render(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.render_scene"
    bl_label = "Render scene"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        global name
        if(mycred.Shot!=""):
           version=get_Shot_version(shots['results'][shot_dict[mycred.Shot]]['id'])
           if(version['count']!=0):
              index=version['count']-1
              version_name=version['results'][index]['name']
              shot_num=int(version_name[version_name.find('v')+2:])+1
              name=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+'v'+(3-len(str(shot_num)))*"0"+str(shot_num)
       
           else:
              name=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+"v001"
           
           render_and_save(name)
           
        else:
            MessageBox("No shot version available","Render")
        return{'FINISHED'}
    
class Render_animation(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.render_animation"
    bl_label = "Render animation"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context): 
        mycred=bpy.context.scene.cred    
        global name
        if(mycred.Shot!=""):
           version=get_Shot_version(shots['results'][shot_dict[mycred.Shot]]['id'])
           if(version['count']!=0):
              index=version['count']-1
              version_name=version['results'][index]['name']
              shot_num=int(version_name[version_name.find('v')+2:])+1
              name=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+'v'+(3-len(str(shot_num)))*"0"+str(shot_num)
       
           else:
              name=mycred.Shot.replace(" ","_")+'.'+mycred.Task.replace(" ","_")+'.'+"v001"
           
           render_anim(name)
           
        else:
            MessageBox("No shot version available","Render")
      
        return{'FINISHED'}
    
class AddUser(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_register"
    bl_label = "Add User"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred 
        global valid           
        valid=get_token(mycred.Email,mycred.Password)
        if(valid):
              MessageBox("Successful","Login")
              bpy.app.timers.register(update)
        else:
              MessageBox("Failed","Login",'ERROR')
         
        return{'FINISHED'}
    
class LogOut(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_logout"
    bl_label = "LogOut"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        mycred.Email=""
        mycred.Password=""
        global Project_names
        Project_names=[]
        global sequences_names
        sequences_names=[]
        global Shot_names
        Shot_names=[]
        global Task_names
        Task_names=[]
        global Asset_names
        Asset_names=[]
        global token
        token=""
        global project
        project={}
        global sequences
        sequences={}
        global shots
        shots={}
        global tasks
        tasks={}
        global asset
        asset={}
        global name
        name=""
        global asset_version
        asset_version={}
        mycred.Asset_version=""
        first_login=0
        bpy.app.timers.unregister(update)
        return{'FINISHED'}

def get_names(self,context):
    return Project_names

def get_sequences_names(self,context):
    return sequences_names

def get_shot_version(self,context):
    return Shot_names

def get_task_name(self,context):
    return Task_names

def get_assets_names(self,context):
    return Asset_names

class Credentials(bpy.types.PropertyGroup):
    
    Project : bpy.props.EnumProperty(
        name = "Projects",
        description = "enum desc",
        items = get_names
    )   
    
    Sequence : bpy.props.EnumProperty(
        name = "Sequences",
        description = "enum desc",
        items = get_sequences_names
    )
    
    Shot : bpy.props.EnumProperty(
        name = "Shots",
        description = "enum desc",
        items = get_shot_version
    )
    
    Task : bpy.props.EnumProperty(
        name = "Tasks",
        description = "enum desc",
        items = get_task_name
    )
    
    Assets_list : bpy.props.EnumProperty(
        name = "Assets",
        description = "enum desc",
        items = get_assets_names
    )
    
    Asset_version : bpy.props.StringProperty(name="Version")
    Email:bpy.props.StringProperty(name="Username")
    Password:bpy.props.StringProperty(name="Password",subtype='PASSWORD')  
       
class LoginPanel(bpy.types.Panel):
    bl_label = "Sequence Tab"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"    
    bl_category  = "MovieColab"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mycred  = scene.cred
        col = layout.column(align=True)
        row = col.row(align=True)
        
        layout.prop(mycred,"Email")
        layout.prop(mycred,"Password")
        row=layout.row()
        row.operator(AddUser.bl_idname, text="Login")
        
        row=layout.row()
        row.operator(ProjectInfo.bl_idname, text="Get Projects")
        layout.prop(mycred,"Project")
        
        row=layout.row()
        row.operator(Sequences.bl_idname, text="Get Sequences")
        layout.prop(mycred,"Sequence")
        
        row=layout.row()
        row.operator(Shot_list.bl_idname, text="Get Shots")
        layout.prop(mycred,"Shot")
        
        row=layout.row()
        row.operator(Tasks.bl_idname, text="Get Tasks Assigned")
        layout.prop(mycred,"Task")
        
        row=layout.row()
        row.operator(Render.bl_idname, text="Render")
        
        row=layout.row()
        row.operator(Create_Shot.bl_idname, text="Upload rendered image")
        
        row=layout.row()
        row.operator(Render_animation.bl_idname, text="Render Sequence")
        
        row=layout.row()
        row.operator(Create_Shot_sequence.bl_idname, text="Upload Sequence")
        
        row=layout.row()
        row.operator(LogOut.bl_idname, text="Log Out")  
        
# Assets Portion

def get_asset_list(project_id):
    r=requests.get(MOVCOLAB_URL+"trackables/asset/?project="+str(project_id),headers={'Authorization':'Bearer '+x})
    return r.json()

def get_asset_versions(id):
    r=requests.get(MOVCOLAB_URL+"trackables/asset-version?asset="+str(id),headers={'Authorization':'Bearer '+x})
    return r.json()

def create_asset_version(name,asset):
    data={ 
    "name": "String", 

    "asset":0, 
    } 
    data["name"]=name
    data["asset"]=asset
    ss_directory=str(directory)+"\\"+str(name)+'.mp4'
    
    if(os.path.isfile(ss_directory)):
      files=[('file',(ss_directory,open(ss_directory,'rb')))]
      r=requests.post(MOVCOLAB_URL+"trackables/asset-version/",headers={'Authorization':'Bearer '+x},data=data,files=files)
      return (r.status_code)
  
    else:
      return 101
        
class Assets(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.user_assets"
    bl_label = "Get assets"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        global asset
        global Asset_names
        Asset_names.clear()
        global asset_dict
        asset_dict.clear()
        if(mycred.Project!=""):
           asset=get_asset_list(project['results'][project_dict[mycred.Project]]['id'])
        
           for i in range(asset['count']):
               asset_dict[asset['results'][i]['name']]=i
        
           for i in range(asset['count']):
               Asset_names.append((asset['results'][i]['name'],asset['results'][i]['name'],""))
        
        else:
            MessageBox("No project available","Assets")

        return{'FINISHED'}

class Asset_Version(bpy.types.Operator):
    bl_idname = "object.user_assets_version"
    bl_label = "Get assets version"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred        
        global asset_version
        if(mycred.Assets_list!=""):
           asset_version=get_asset_versions(asset['results'][asset_dict[mycred.Assets_list]]['id'])
           if(asset_version['count']!=0):
              index=asset_version['count']-1
              mycred.Asset_version=asset_version['results'][index]['name']
           
           else:
              mycred.Asset_version="" 
        
        else:
            mycred.Asset_version="" 
            MessageBox("No assets available","Asset Version")
        return{'FINISHED'}
    
class Render_asset(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.render_asset_animation"
    bl_label = "Render asset animation"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context): 
        mycred=bpy.context.scene.cred
        global name_asset 
        if(mycred.Assets_list!=""):
           if(asset_version['count']!=0):
              version_name=mycred.Asset_version
              shot_num=int(version_name[version_name.find('v')+2:])+1
              name_asset=mycred.Assets_list.replace(" ","_")+'.'+'v'+(3-len(str(shot_num)))*"0"+str(shot_num)
       
           else:
              name_asset=mycred.Assets_list.replace(" ","_")+'.'+"v001"  
           render_anim(name_asset)
           
        else:
           MessageBox("No assets available","Render")
        return{'FINISHED'}

class upload_asset_sequence(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.upload_asset_sequence"
    bl_label = "Upload asset sequence"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mycred=bpy.context.scene.cred
        if(mycred.Assets_list!=""):
           Asset=asset['results'][asset_dict[mycred.Assets_list]]['id']
        
           if(asset_version['count']!=0):
             version_name=mycred.Asset_version
             shot_num=int(version_name[version_name.find('v')+2:])+1
             Name=mycred.Assets_list.replace(" ","_")+'.'+'v'+(3-len(str(shot_num)))*"0"+str(shot_num)
       
           else:
             Name=mycred.Assets_list.replace(" ","_")+'.'+"v001"  
           
           statuscode=create_asset_version(Name,Asset)
        
           if(statuscode==401):
              MessageBox("Failed","Asset Sequence upload",'ERROR')
        
           elif(statuscode==201):
              MessageBox("Success","Asset Sequence upload")
        
           elif(statuscode==101):
              MessageBox("No such file in the directory","Asset Sequence upload")
           
        else:
              MessageBox("No sequence to upload","Asset Sequence upload")
        return{'FINISHED'}

def update():
    mycred=bpy.context.scene.cred
    if (first_login==1):
        get_token(mycred.Email,mycred.Password)
        
    return 300
                      
class AssetPanel(bpy.types.Panel):
    bl_label = "Asset Tab"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"    
    bl_category  = "MovieColab"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mycred  = scene.cred
        col = layout.column(align=True)
        row = col.row(align=True) 
        layout.label(text=mycred.Email)
        
        row=layout.row()
        row.operator(ProjectInfo.bl_idname, text="Get Projects")
        layout.prop(mycred,"Project")
        
        row=layout.row()
        row.operator(Assets.bl_idname, text="Get Assets")
        layout.prop(mycred,"Assets_list")
        
        row=layout.row()
        row.operator(Asset_Version.bl_idname, text="Get Asset Version")
        layout.prop(mycred,"Asset_version")
        
        row=layout.row()
        row.operator(Render_asset.bl_idname, text="Render asset Sequence")
        
        row=layout.row()
        row.operator(upload_asset_sequence.bl_idname, text="Upload Sequence")

                   
classes = [Credentials,LoginPanel,AssetPanel,AddUser,ProjectInfo,Sequences,Assets,Asset_Version,Render_asset,upload_asset_sequence,Shot_list,Tasks,Render,Create_Shot,Render_animation,Create_Shot_sequence,LogOut]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cred = bpy.props.PointerProperty(type = Credentials)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cred


if __name__ == "__main__":
    register()
    
      