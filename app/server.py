from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO

from fastai import *
from fastai.vision import *

#model_file_url = 'https://www.dropbox.com/s/q0nuw0gvjghpbdg/stage-2.pth?raw=1'
#model_file_name = 'model'
#classes = ['black', 'grizzly', 'teddys']

model_file_url = 'https://www.dropbox.com/s/0jbw7s74yu4t52d/stage-3.pth?raw=1'
model_file_name = 'model4'
classes = ['9326871', '9332898', '9336923', '9338446', '9338454', '9338462', '9338489', '9338497', '9338519', '9338527', '9338535', '9338543', '9414649', '9416994', 'admars', 'ahodki', 'ajflem', 'ajones', 'ajsega', 'akatsi', 'ambarw', 'anpage', 'asamma', 'asewil', 'asheal', 'astefa', 'bplyce', 'cchris', 'ccjame', 'cferdo', 'cgboyc', 'cjcarr', 'cjdenn', 'cjsake', 'cmkirk', 'csanch', 'cshubb', 'cwchoi', 'dagran', 'dakram', 'dcbowe', 'dioann', 'djbirc', 'djhugh', 'djmart', 'dmwest', 'drbost', 'ekavaz', 'elduns', 'gdhatc', 'ggeorg', 'ggrego', 'gjhero', 'gjnorm', 'gmwate', 'gpapaz', 'gpsmit', 'gsreas', 'irdrew', 'jabins', 'jagrif', 'jcarte', 'jdbenm', 'jgloma', 'jlemon', 'jmedin', 'jrtobi', 'kaatki', 'kaknig', 'kdjone', 'khchan', 'khughe', 'kjwith', 'klclar', 'ksunth', 'lejnno', 'lfso', 'maasht', 'mberdo', 'mbutle', 'mdpove', 'mefait', 'mhwill', 'miaduc', 'mjhans', 'mpetti', 'muthay', 'nahaig', 'namull', 'ndbank', 'ndhagu', 'nhrams', 'njmoor', 'npbour', 'npmitc', 'nrclar', 'nrrbar', 'nwilli', 'ohpark', 'pacole', 'phughe', 'pmives', 'pshurr', 'pspliu', 'ptnich', 'rarobi', 'rgharr', 'rgspru', 'rjlabr', 'rlocke', 'rmcoll', 'rmpugh', 'rnpwil', 'rrowle', 'rsanti', 'saduah', 'saedwa', 'sbains', 'sidick', 'sjbeck', 'skumar', 'slbirc', 'smrobb', 'spletc', 'svkriz', 'swewin', 'swsmit', 'vpsavo', 'vstros', 'whussa', 'wjalbe', 'yfhsie']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():
    await download_file(model_file_url, path/'models'/f'{model_file_name}.pth')
    data_bunch = ImageDataBunch.single_from_classes(path, classes,
        ds_tfms=get_transforms(), size=224).normalize(imagenet_stats)
    learn = cnn_learner(data_bunch, models.resnet34, pretrained=False)
    learn.load(model_file_name)
    return learn

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    losses = str(trained_model.predict(img)[2])
    losses = losses.replace('\n        ','').replace('tensor','').replace('(','').replace(')','').replace('[','').replace(']','')
    mylist = [float(x) for x in losses.split(',')]
    predictions = sorted(zip(dataClasses, mylist), key=lambda p: p[1], reverse=True)
    st = predictions[0]
    nd = predictions[1]
    rd = predictions[2]
    resultText = st + " " + nd + " " + rd
    return JSONResponse({'result': str(resultText)})
    #return JSONResponse({'result': str(learn.predict(img)[0])})
    #_,_,losses = learn.predict(img)[0]
    #predictions = sorted(zip(classes, map(float, losses)), key=lambda p: p[1], reverse=True)
    #st = str([i for i,j in predictions[0:1]]) + " - " + str([j for i,j in predictions[0:1]])
    #nd = str([i for i,j in predictions[1:2]]) + " - " + str([j for i,j in predictions[1:2]])
    #rd = str([i for i,j in predictions[2:3]]) + " - " + str([j for i,j in predictions[2:3]])
    #st = st.replace('[','')
    #st = st.replace(']','')
    #st = st.replace("'","")
    #nd = nd.replace('[','')
    #nd = nd.replace(']','')
    #nd = nd.replace("'","")
    #rd = rd.replace('[','')
    #rd = rd.replace(']','')
    #rd = rd.replace("'","")
    #resultText = str("1st:" + st + " 2nd:" + nd + " 3rd:" + rd)
    #return JSONResponse({'result': str(resultText)})

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app, host='0.0.0.0', port=8080)

