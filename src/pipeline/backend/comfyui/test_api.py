import json
from urllib import request, parse
import random
import websocket
import uuid 
import os
from PIL import Image
import io

#This is the ComfyUI api prompt format.

#If you want it for a specific workflow you can "enable dev mode options"
#in the settings of the UI (gear beside the "Queue Size: ") this will enable
#a button on the UI to save workflows in api format.

#keep in mind ComfyUI is pre alpha software so this format will change a bit.
#this is the one for the default workflow

def track_progress(prompt, ws, prompt_id):
  node_ids = list(prompt.keys())
  finished_nodes = []

  while True:
      out = ws.recv()
      if isinstance(out, str):
          message = json.loads(out)
          print('!!!!!!!!', message['type'])
          if message['type'] == 'progress':
              data = message['data']
              current_step = data['value']
              print('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
          if message['type'] == 'execution_cached':
              data = message['data']
              for itm in data['nodes']:
                  if itm not in finished_nodes:
                      finished_nodes.append(itm)
                      print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')
          if message['type'] == 'executing':
              data = message['data']
              if data['node'] not in finished_nodes:
                  finished_nodes.append(data['node'])
                  print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')

              if data['node'] is None and data['prompt_id'] == prompt_id:
                  break #Execution is done
      else:
          continue
  return

def show_gif(fname):
    import base64
    from IPython import display
    with open(fname, 'rb') as fd:
        b64 = base64.b64encode(fd.read()).decode('ascii')
    return display.HTML(f'<img src="data:image/gif;base64,{b64}" />')

def open_websocket_connection():
  server_address='127.0.0.1:8188'
  #server_address='0.0.0.0:8189'
  client_id=str(uuid.uuid4())
  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  return ws, server_address, client_id

def get_history(prompt_id, server_address):
  with request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
      data = json.loads(response.read())
      return data

def get_image(filename, subfolder, folder_type, server_address):
  data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
  url_values = parse.urlencode(data)
  with request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
      return response.read()

def get_images(prompt_id, server_address):
  output_images = {}
  history = get_history(prompt_id, server_address)[prompt_id]
  for node_id in history['outputs']:
      node_output = history['outputs'][node_id]
      print(node_id, node_output) 
      if 'images' in node_output:
          images_output = []
          for image in node_output['images']:
              image_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
              images_output.append(image_data)
          output_images[node_id] = images_output
      if 'videos' in node_output:
          videos_output = []
          for video in node_output['videos']:
              video_data = get_image(video['filename'], video['subfolder'], video['type'], server_address)
              videos_output.append(video_data)
          output_images[node_id] = videos_output
      if 'gifs' in node_output:
          gifs_output = []
          for gif in node_output['gifs']:
              gif_data = get_image(gif['filename'], gif['subfolder'], gif['type'], server_address)
              gifs_output.append(gif_data)
          output_images[node_id] = gifs_output
  #print(output_images)
  return output_images

def save_image(images, output_path, save_previews):
  for node_id in images:
    for image_data in images[node_id]:
      itm = json.loads(image_data)
      directory = os.path.join(output_path, 'temp/') if itm['type'] == 'temp' and save_previews else output_path
      os.makedirs(directory, exist_ok=True)
      try:
          image = Image.open(io.BytesIO(itm['image_data']))
          image.save(os.path.join(directory, itm['file_name']))
      except Exception as e:
          print(f"Failed to save image {itm['file_name']}: {e}")  

def queue_prompt(prompt, client_id, server_address):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req =  request.Request("http://{}/prompt".format(server_address), data=data, headers=headers)
    return json.loads(request.urlopen(req).read())
    #request.urlopen(req)

f = open('./workflow_txt2img_ltx_video_api.json')
prompt = json.load(f)



ws, server_address, client_id = open_websocket_connection()
prompt_id = queue_prompt(prompt, client_id, server_address)['prompt_id']
print(prompt_id)
track_progress(prompt, ws, prompt_id) 
#images = get_images(prompt_id, server_address)

#output_path = './output'
#save_image(images, output_path, save_previews=False)

