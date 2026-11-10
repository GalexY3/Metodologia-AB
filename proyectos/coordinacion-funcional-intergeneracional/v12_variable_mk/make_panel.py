"""Build offline interactive HTML from actual V12 histories, evals and frozen replay."""
from pathlib import Path
from dataclasses import replace
import json,torch
from v12 import ROOT,Config,IndividualAgent,evaluate
torch.set_num_threads(3)
runs={}
for folder in sorted((ROOT/'runs').glob('v12_*')):
    h=folder/'history.jsonl'
    if not h.exists():continue
    lines=[json.loads(x) for x in h.read_text('utf8').splitlines() if x.strip()]
    if not lines:continue
    runs[folder.name]={'history':lines,
                      'config':json.loads((folder/'config.json').read_text('utf8')),
                      'replays':{}}
    if not (folder/'latest.pt').exists():continue
    # Select small subset of replayed societies, never fabricated frames.
    if folder.name not in ('v12_long_n60_c0_s3111','v12_long_n60_c1_s3111',
                            'v12_long_n120_c0pub_s3111','v12_ext_n60_c0_s3111',
                            'v12_ext_n120_c0pub_s3111'):
        continue
    st=torch.load(folder/'latest.pt',map_location='cpu',weights_only=False)
    saved=runs[folder.name]['config']['config']
    cfg=Config(**{**saved,'device':'cpu'})
    model=IndividualAgent(cfg.n)
    model.load_state_dict(st['model'])
    model.eval()
    for label,m,k in [('conocido',10,2),('transferencia',30,5)]:
        if cfg.n%k:continue
        c=replace(cfg,m=m,k=k,init='random')
        x=evaluate(model,c,seed=977711,batch=1,horizon=60,record=True)
        runs[folder.name]['replays'][label]=dict(
          m=m,k=k,n=cfg.n,frames=x['frames'],final=x['final'])
    print('REPLAY',folder.name,len(runs[folder.name]['replays']),flush=True)
evals={}
for file in ROOT.glob('*_TRANSFER.json'):
    obj=json.loads(file.read_text('utf8'))
    for item in obj['models']:
        evals[item['name']]=item['tests']
payload=json.dumps(dict(runs=runs,evals=evals),ensure_ascii=False).replace('</','<\\/')
html=r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Investigación MARL · aldea variable</title><style>
:root{color-scheme:dark;--bg:#0b1623;--card:#19283a;--ink:#e9f2fe;--muted:#b1c1cf;--line:#395164}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:1320px;margin:auto;padding:25px 18px 80px}h1{font-size:clamp(27px,3vw,42px);margin:2px 0 8px}
h2{font-size:20px;margin:0 0 10px}p{color:var(--muted);margin:3px 0 12px}
.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#7fddce;font-weight:700}
.panel{margin:16px 0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
label{color:var(--muted);font-size:13px}select,button{background:#283f56;color:var(--ink);border:1px solid #617485;border-radius:7px;padding:8px;cursor:pointer}
input[type=range]{width:100%;accent-color:#7bdbcb}canvas{width:100%;height:250px;display:block}
table{border-collapse:collapse;width:100%;font-size:13px;white-space:nowrap}th,td{padding:9px 8px;text-align:left;border-bottom:1px solid #33495c}th{color:#a3bfcd}.scroll{overflow-x:auto}
#people{display:grid;gap:2px;max-width:580px;margin:12px auto}.person{aspect-ratio:1;border-radius:2px}
#bars{display:flex;align-items:end;gap:3px;height:160px;border-bottom:1px solid #627687}
.bar{min-width:0;flex:1;border-radius:3px 3px 0 0}.note{font-size:12px;color:var(--muted)}
@media(max-width:800px){.grid{grid-template-columns:1fr}main{padding:12px}}
</style></head><body><main>
<div class="eyebrow">Investigación · recompensas individuales · agentes independientes</div>
<h1>La aldea descubre profesiones</h1>
<p>Modelo variable: 10, 20, 30 o 50 profesiones; objetivos sostenibles de 2, 3, 4, 5, 6 o 10 grupos. Las redes individuales no conocen la cuota óptima ni la distribución total. Los fotogramas proceden de modelos congelados y sociedades realmente simuladas.</p>
<div class="panel"><h2>Evolución del entrenamiento</h2><div class="controls"><label>Modelo</label><select id="model"></select>
<label>Medida</label><select id="metric"><option value="food">Alimentación</option><option value="d">Distancia distributiva</option><option value="occupied">Profesiones ocupadas</option></select></div>
<canvas id="curve"></canvas><p class="note">Línea verde: M=10, k=2, presente en entrenamiento. Línea azul: M=30, k=5, excluido del entrenamiento. Son evaluaciones repetidas de desarrollo, no un holdout sellado.</p></div>
<div class="grid"><div class="panel"><h2>Sociedad y decisiones</h2><div class="controls">
<label>Escenario</label><select id="scenario"><option value="conocido">M=10, k=2</option><option value="transferencia">M=30, k=5</option></select>
<button id="prev">Anterior</button><button id="next">Siguiente</button><button id="play">Reproducir</button></div>
<input id="scrub" type="range" min="0" max="60" value="0"><p id="frameInfo"></p><div id="people"></div>
<p class="note">Los cuadrados son habitantes ordenados por identificador, no posiciones geográficas del grafo social.</p></div>
<div class="panel"><h2>Ocupación de los grupos</h2><div id="bars"></div><p id="occupations"></p>
<p class="note">El resultado ideal sería k barras de altura N/k y las demás vacías. El nombre de las profesiones es arbitrario.</p>
<h2>Información disponible</h2><p>La red observa profesiones vecinas, alimento propio y experiencia acumulada. El tratamiento público añade alimento medio de la aldea. Los anuncios de intención son voluntarios y su utilización debe demostrarse causalmente.</p></div></div>
<div class="panel"><h2>Evaluación en mundos nuevos</h2><div class="scroll"><table><thead><tr><th>Escenario</th><th>Evaluación</th><th>Raciones</th><th>Distancia</th><th>Repartos exactos</th></tr></thead><tbody id="results"></tbody></table></div>
<p class="note">Los checkpoints fueron seleccionados mediante desarrollo previo; las evaluaciones posteriores tienen semillas nuevas, pero todavía son exploratorias.</p></div>
</main><script>
const D=__DATA__;
const $=id=>document.getElementById(id);
const names=Object.keys(D.runs).sort();
const color=i=>'hsl('+((i*137.508)%360).toFixed(2)+' 66% 60%)';
let chosen=names.find(x=>x==='v12_long_n60_c0_s3111')||names[0],index=0,timer=null;
function format(x,n=3){return Number(x).toFixed(n)}
function uiModel(){let html='';for(const n of names)html+='<option value="'+n+'">'+n+'</option>';$('model').innerHTML=html;$('model').value=chosen}
function plot(){const canvas=$('curve'),c=canvas.getContext('2d'),w=canvas.clientWidth||650,h=250,dpr=window.devicePixelRatio||1;
canvas.width=w*dpr;canvas.height=h*dpr;c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);
const key=$('metric').value,rows=D.runs[chosen].history,maxx=Math.max(1,...rows.map(x=>x.update));
const maxY=key==='occupied'?50:1,x=t=>44+(t/maxx)*(w-62),y=v=>15+(maxY-v)/maxY*(h-44);
c.strokeStyle='#43596e';c.fillStyle='#b7c9d9';c.font='12px system-ui';
for(let j=0;j<=5;j++){const v=j*maxY/5;const py=y(v);c.beginPath();c.moveTo(44,py);c.lineTo(w-15,py);c.stroke();c.fillText(v.toFixed(key==='occupied'?0:1),3,py+3)}
for(const [scenario,col] of [['train_k2_m10','#7dd4a6'],['new_k5_m30','#79bbed']]){
c.strokeStyle=col;c.lineWidth=2.5;c.beginPath();let count=0;
for(const row of rows){const obj=row.evaluations[scenario];if(!obj)continue;const yy=y(obj[key]);if(!count)c.moveTo(x(row.update),yy);else c.lineTo(x(row.update),yy);count++}c.stroke()}
}
function getReplay(){return D.runs[chosen].replays[$('scenario').value]}
function stop(){if(timer){clearInterval(timer);timer=null;$('play').textContent='Reproducir'}}
function draw(){let r=getReplay();if(!r){$('people').innerHTML='';$('frameInfo').textContent='Este modelo no tiene reproducción exportada';return}
index=Math.max(0,Math.min(index,r.frames.length-1));$('scrub').max=r.frames.length-1;$('scrub').value=index;
const f=r.frames[index],n=f.states.length,side=Math.ceil(Math.sqrt(n));
$('frameInfo').textContent='Turno '+f.t+' · N='+n+' · M='+f.m+' · k='+f.k+' · alimentación '+format(f.food);
$('people').style.gridTemplateColumns='repeat('+side+',minmax(0,1fr))';
$('people').innerHTML=f.states.map((job,i)=>'<div class="person" title="Habitante '+i+' · profesión '+job+'" style="background:'+color(job)+'"></div>').join('');
const largest=Math.max(1,...f.counts);
$('bars').innerHTML=f.counts.map((num,i)=>'<div class="bar" title="Profesión '+i+' = '+num+'" style="background:'+color(i)+';height:'+Math.max(1,num/largest*100)+'%"></div>').join('');
$('occupations').textContent='Ocupación: '+f.counts.map((num,i)=>num>0?i+': '+num:'').filter(Boolean).join(' · ')
}
function renderTable(){const rows=D.evals[chosen]||[];
$('results').innerHTML=rows.map(r=>'<tr><td>'+r.task+'</td><td>'+r.mode+'</td><td>'+format(r.mean_food)+'</td><td>'+format(r.mean_d)+'</td><td>'+r.exact+'/'+r.total_worlds+'</td></tr>').join('')||'<tr><td>Sin evaluación cruzada registrada</td></tr>'}
$('model').onchange=()=>{chosen=$('model').value;index=0;stop();plot();draw();renderTable()};
$('scenario').onchange=()=>{index=0;stop();draw()};
$('metric').onchange=plot;$('scrub').oninput=()=>{index=+$('scrub').value;draw()};
$('prev').onclick=()=>{index--;draw()};$('next').onclick=()=>{index++;draw()};
$('play').onclick=()=>{if(timer){stop();return}timer=setInterval(()=>{let r=getReplay();if(!r||index>=r.frames.length-1){stop();return}index++;draw()},180);$('play').textContent='Pausar'};
window.onresize=plot;uiModel();plot();draw();renderTable();
</script></body></html>'''
text=html.replace('__DATA__',payload)
(ROOT/'PANEL_ALDEA_VARIABLE.html').write_text(text,encoding='utf8')
print('PANEL_READY',len(runs),'runs',len(evals),'evals',len(text),'bytes')
