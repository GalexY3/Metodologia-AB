"""Offline interactive panel displaying REAL frozen rollout frames for varied k."""
from pathlib import Path
from dataclasses import replace
import json,math
import torch
import train_k
old=train_k.old
HERE=Path(__file__).resolve().parent
def validate_any(c):
    if not 2<=c.k<=c.m<=80:raise ValueError('k exceeds available professions')
    if c.n<12 or c.n%2:raise ValueError('invalid N')
    if not 1<=c.degree<c.n:raise ValueError('degree')
old.validate=validate_any
torch.set_num_threads(3)
names=['v14_N120_knownK_s3111','v14_N120_hiddenK_s3111','v14_N120_curriculum_k2to15_s3111','v14_N120_fullrange_s3111']
ks=[2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,19,20,24,29,30]
payload=[]
for name in names:
    f=HERE/'runs'/name
    spec=json.loads((f/'config.json').read_text('utf8'))
    mask=json.loads((f/'V14_MODEL_SPEC.json').read_text('utf8'))['knows_requested_k']
    train_k.configure(mask)
    cfg=old.Config(**{**spec['config'],'device':'cpu'})
    a=train_k.Actor(cfg.n)
    st=torch.load(f/'latest.pt',map_location='cpu',weights_only=False)
    a.load_state_dict(st['model']);a.eval()
    simulations={}
    for k in ks:
        c=replace(cfg,m=80,k=k,batch=1,horizon=80,init='random')
        with torch.no_grad():
            x=old.evaluate(a,c,seed=992719,batch=1,horizon=80,record=True)
        frames=x['frames']
        frames=[dict(t=v['t'],states=v['states'],counts=v['counts'],food=v['food']) for v in frames]
        simulations[str(k)]=frames
        print('REPLAY',name,'k',k,'food',round(frames[-1]['food'],4),flush=True)
    payload.append(dict(name=name,known_k=mask,train_k=sorted(set(k for m,k in spec['tasks'])),
                        updates=st['update'],simulations=simulations))
data=json.dumps({'models':payload,'n':120,'m':80,'seed':992719},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
html=r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Aldea V14 · ¿puede aprender cualquier k?</title>
<style>
:root{color-scheme:dark;--bg:#101923;--p:#1b2c3e;--edge:#3a5268;--fg:#e8f2ff;--muted:#a9c0d2}
*{box-sizing:border-box}body{font:15px/1.5 system-ui,Segoe UI,sans-serif;background:var(--bg);color:var(--fg);margin:0}
main{max-width:1290px;margin:auto;padding:25px 16px 50px}
h1{font-size:clamp(25px,3vw,40px);margin:4px 0 10px}h2{font-size:19px;margin:0 0 10px}
p{color:var(--muted);margin:6px 0 12px}.eyebrow{font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:#78d4bc;font-weight:700}
.panel{background:var(--p);padding:17px;border:1px solid var(--edge);border-radius:13px;margin-top:15px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.controls{display:flex;gap:13px;align-items:end;flex-wrap:wrap}
select,button{background:#314b63;border:1px solid #64819b;color:var(--fg);border-radius:7px;padding:9px;cursor:pointer}
label{display:block;font-size:12px;color:var(--muted)}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0}
.metric{padding:10px;border:1px solid #3c556b;background:#142434;border-radius:8px}
.metric span{font-size:12px;color:var(--muted);display:block}.metric b{font-size:20px}
#people{display:grid;gap:2px;margin:12px auto;max-width:540px}.agent{aspect-ratio:1;border-radius:3px}
#bars{display:flex;gap:2px;align-items:end;height:135px;border-bottom:1px solid #8298ac}
.bar{min-width:0;flex:1;border-radius:2px 2px 0 0}
canvas{height:225px;display:block;width:100%}#scrub{width:100%;accent-color:#7bcdb9}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:9px 0}small{font-size:11px;color:var(--muted)}
@media(max-width:850px){.grid{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}
</style></head><body><main><div class="eyebrow">Aprendizaje multiagente individual · generalización zero-shot por objetivo</div>
<h1>La aldea ante cualquier número de grupos</h1>
<p>Los tres modelos se entrenaron con redes neuronales y recompensas individuales. Cada habitante tiene 225 parámetros propios. Elige un valor de k y observa si forman exactamente k profesiones con aproximadamente N/k habitantes por profesión. Las imágenes son fotogramas de evaluaciones reales con los pesos congelados.</p>
<div class="panel"><div class="controls">
<div><label>Política neuronal</label><select id="policy"></select></div>
<div><label>Profesiones necesarias, k</label><select id="k"></select></div>
<div><label>Fotograma</label><button id="prev">Anterior</button> <button id="next">Siguiente</button> <button id="play">Reproducir</button></div>
</div><p id="context"></p>
<input id="scrub" type="range" value="0" min="0" max="80"/><small id="timeLabel"></small>
<div class="metrics">
<div class="metric"><span>Ración media (máx. cercano a 1)</span><b id="food">–</b></div>
<div class="metric"><span>Profesiones ocupadas</span><b id="active">–</b></div>
<div class="metric"><span>Profesiones con ≥ media cuota</span><b id="substantial">–</b></div>
<div class="metric"><span>Reparto exacto</span><b id="exact">–</b></div>
</div></div>
<div class="grid"><div class="panel"><h2>Habitantes, coloreados por profesión</h2><div id="people"></div><p><small>Los cuadros representan identificadores de agentes ordenados en filas; no son una representación de sus posiciones sociales o geográficas.</small></p></div>
<div class="panel"><h2>Reparto entre profesiones</h2><div id="bars"></div><p id="occupationText"></p><p>Una solución exacta contiene exactamente k profesiones ocupadas, con N/k personas cada una si la cuota es entera, o tamaños que difieren como máximo en una persona si la cuota no es entera.</p><p>La figura permite distinguir una concentración útil para sobrevivir de una verdadera adaptación al objetivo solicitado.</p></div></div>
<div class="panel"><h2>Evolución del alimento y aproximación al objetivo</h2><canvas id="curve"></canvas><p><small>Línea verde: alimento medio. Línea azul: distancia distributiva D al objetivo de k profesiones (menor es mejor). Para cuotas fraccionarias, D=0 puede no ser alcanzable.</small></p></div>
<div class="panel"><h2>Cómo interpretar los resultados</h2><p>La política «k visible» entrenó con k=2,3,4,6; el «control sin k» con esos mismos valores sin recibir la instrucción; el «currículo ampliado» añadió k=10,15. El «rango amplio» empezó de cero e incluyó k=24,30. Todos los casos representados utilizan 80 profesiones posibles, cifra no empleada en actualizaciones de entrenamiento.</p><p>Solo una sociedad por k es visible en este panel. Los resultados cuantitativos de comparación corresponden a 144 sociedades por condición y se conservan por separado en archivos JSON. Un ejemplo vistoso no es una prueba de generalización.</p></div>
</main><script>
const D=__DATA__;
const $=name=>document.getElementById(name);
const color=i=>'hsl('+((i*137.507764+23)%360)+' 72% 60%)';
let model=D.models[0],k='5',t=0,timer=null;
function frame(){return model.simulations[k]?.[t]}
function stop(){if(timer){clearInterval(timer);timer=null;$('play').textContent='Reproducir'}}
function setup(){
$('policy').innerHTML=D.models.map((m,i)=>'<option value="'+i+'">'+['k visible, 1.400 updates','control sin k, 1.400 updates','currículo hasta k=15, 3.000 updates','rango amplio hasta k=30, 3.500 updates'][i]+'</option>').join('');
$('k').innerHTML=Object.keys(D.models[0].simulations).map(k=>'<option value="'+k+'">'+k+'</option>').join('');
$('k').value=k;$('policy').value=0;draw()}
function draw(){
const all=model.simulations[k];if(!all)return;
t=Math.max(0,Math.min(t,all.length-1));let f=frame(),n=f.states.length,quota=n/+k;
$('scrub').max=all.length-1;$('scrub').value=t;
$('timeLabel').textContent='Turno '+t+' de '+(all.length-1);
const active=f.counts.filter(x=>x>0),positive=active.length;
const substantial=active.filter(x=>x>=quota/2).length;
const exact=positive==+k&&Math.max(...active)-Math.min(...active)<=1;
$('context').textContent='Población N='+n+' · Profesiones posibles M=80 · Objetivo k='+k+
' · Cuota N/k='+quota.toFixed(2)+' · '+(model.train_k.includes(+k)?'k presente en entrenamiento':'k excluido del entrenamiento')+
' · '+(model.known_k?'objetivo visible':'objetivo oculto');
$('food').textContent=f.food.toFixed(3);$('active').textContent=positive;
$('substantial').textContent=substantial;$('exact').textContent=exact?'SÍ':'NO';
$('people').style.gridTemplateColumns='repeat(12,minmax(0,1fr))';
$('people').innerHTML=f.states.map((role,i)=>'<div title="Agente '+i+' · profesión '+role+'" class="agent" style="background:'+color(role)+'"></div>').join('');
let roles=f.counts.map((v,j)=>({v,j})).filter(x=>x.v).sort((a,b)=>b.v-a.v);
let top=Math.max(1,...roles.map(x=>x.v));
$('bars').innerHTML=roles.map(x=>'<div class="bar" title="Profesión '+x.j+': '+x.v+' habitantes" style="background:'+color(x.j)+';height:'+Math.max(1,x.v/top*100)+'%"></div>').join('');
$('occupationText').textContent=roles.slice(0,16).map(x=>'P'+x.j+': '+x.v).join(' · ')+(roles.length>16?' · …':'');
plot(all)
}
function dist(f){let sizes=[...f.counts].sort((a,b)=>b-a).slice(0,+k);return 1-sizes.reduce((a,b)=>a+Math.min(b,D.n/+k),0)/D.n}
function plot(steps){
let canvas=$('curve'),c=canvas.getContext('2d'),w=canvas.clientWidth||800,h=225,r=window.devicePixelRatio||1;
canvas.width=w*r;canvas.height=h*r;c.setTransform(r,0,0,r,0,0);c.clearRect(0,0,w,h);
let x=i=>36+i/(steps.length-1)*(w-48),y=v=>10+(1-v)*(h-40);
c.strokeStyle='#475c70';c.fillStyle='#aec7d8';c.font='11px system-ui';
for(let j=0;j<=5;j++){let v=j/5,yy=y(v);c.beginPath();c.moveTo(36,yy);c.lineTo(w-10,yy);c.stroke();c.fillText(v.toFixed(1),4,yy+4)}
for(let [fn,col] of [[f=>f.food,'#7ce0aa'],[dist,'#81b8ed']]){
c.strokeStyle=col;c.lineWidth=2.2;c.beginPath();
steps.forEach((f,i)=>{if(i===0)c.moveTo(x(i),y(fn(f)));else c.lineTo(x(i),y(fn(f)))});c.stroke()}
c.strokeStyle='#f8dfaa';c.beginPath();c.moveTo(x(t),10);c.lineTo(x(t),h-30);c.stroke()
}
$('policy').onchange=()=>{model=D.models[+$('policy').value];t=0;stop();draw()};
$('k').onchange=()=>{k=$('k').value;t=0;stop();draw()};
$('scrub').oninput=()=>{t=+$('scrub').value;draw()};
$('prev').onclick=()=>{t--;draw()};$('next').onclick=()=>{t++;draw()};
$('play').onclick=()=>{if(timer){stop();return}timer=setInterval(()=>{if(t>=model.simulations[k].length-1){stop();return}t++;draw()},160);$('play').textContent='Pausar'};
window.onresize=()=>draw();
setup()
</script></body></html>'''
(HERE/'PANEL_K_UNIVERSAL.html').write_text(html.replace('__DATA__',data),encoding='utf8')
print('K_PANEL_READY',len(payload),'models',len(ks),'requested_k',len(data),'embedded JSON characters',flush=True)
