"""Standalone offline viewer using REAL V15 checkpoint rollouts, not a synthetic demo."""
from pathlib import Path
from dataclasses import replace
import json,numpy as np,torch
import v15
from evaluate_v15 import baseline_analytic
HERE=Path(__file__).resolve().parent
torch.set_num_threads(3)
MODELS=('v15_ops_rnn24_s3111','v15_ops_mlp16_s4111')
CASES=((12,8),(12,10),(12,12),(16,15),(24,4),(24,5),(24,12),(24,20),(24,24),
       (32,24),(40,5),(40,20),(48,40),(60,60),(72,60),
       (80,2),(80,5),(80,8),(80,12),(80,20),(80,30),(80,40),(80,60))
def simulate(model,c,seed=2026203,steps=85):
    e=v15.envlib.World(c,seed)
    model.reset()
    frames=[]
    def snap():
        counts=e.counts[0].detach().cpu().numpy().astype(int)
        food=float(e.food[0].mean())
        occupied=int((counts>0).sum())
        nonzero=counts[counts>0]
        frames.append(dict(t=e.t,counts=counts.tolist(),jobs=e.jobs[0].tolist(),
               food=food,occupied=occupied,
               exact=bool(occupied==c.k and int(nonzero.max()-nonzero.min())<=1),
               d=float(1-np.minimum(np.sort(counts)[::-1][:c.k],c.n/c.k).sum()/c.n)))
    with torch.no_grad():
        snap()
        for _ in range(steps):
            tenure=model.tenure.clone() if model.tenure is not None else None
            next_role,_,_=model.act(e,greedy=(c.k/c.m>=.5))
            if c.k/c.m>=.7:
                accept=torch.where(e.food>=.75,e.jobs,next_role)
                if tenure is not None:
                    changed=accept!=e.jobs
                    model.tenure=torch.where(changed,torch.zeros_like(tenure),tenure+1)
                    model.was_moving=changed.float()
                next_role=accept
            e.advance(next_role)
            snap()
    return frames
bundle=[]
for name in MODELS:
    root=HERE/'runs'/name
    spec=json.loads((root/'spec.json').read_text('utf8'))['args']
    model=v15.OptionActor(spec['n'],spec['h'],recurrent=not spec['no_recurrence'])
    ck=torch.load(root/'latest.pt',map_location='cpu',weights_only=False)
    model.load_state_dict(ck['model'])
    model.eval()
    panels={}
    for m,k in CASES:
        c=v15.envlib.Config(n=spec['n'],m=m,k=k,batch=1,horizon=85,degree=spec['degree'])
        fs=simulate(model,c)
        panels[f'{m}_{k}']=dict(m=m,k=k,q=c.n/c.k,
            random=baseline_analytic(c.n,m,k),
            frames=fs,
            k_trained=(k in {int(kk) for pair in json.loads((root/'spec.json').read_text('utf8'))['pairs'] for kk in [pair[1]]}))
    bundle.append(dict(name=name,updates=ck['update'],hidden=spec['h'],
                       recurrent=not spec['no_recurrence'],scenarios=panels))
    print('CHECKPOINT_REPLAYED',name,len(panels),flush=True)
data=json.dumps(dict(n=120,models=bundle,
  warning='Single exemplar per case, not a statistical average. Gate threshold .75 when k/m >=.70. K/M >=.5 selects argmax otherwise sampling.'),separators=(',',':')).replace('</','<\\/')
html=r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>V15 | Aprendizaje neuronal de profesiones para k variable</title>
<style>
:root{color-scheme:dark;--bg:#0c1520;--card:#192a3c;--line:#364f65;--fg:#e9f2ff;--muted:#aabed2;--accent:#85d5bf}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.54 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1390px;margin:auto;padding:23px 18px 54px}.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-weight:750;font-size:11px;color:var(--accent)}
h1{font-size:clamp(26px,3vw,39px);margin:3px 0 9px}h2{font-size:19px;margin:0 0 8px}h3{font-size:15px}
p{color:var(--muted);margin:5px 0 13px}.card{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:17px;margin:14px 0}
.controls{display:flex;gap:13px;align-items:end;flex-wrap:wrap}.field{display:flex;flex-direction:column;gap:5px}
.field label,small{color:var(--muted);font-size:12px}
select,button{background:#30475e;border:1px solid #55738d;color:var(--fg);border-radius:7px;padding:9px;cursor:pointer}
button:hover{background:#41617c}.grid{display:grid;grid-template-columns:1.1fr .9fr;gap:14px}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.metric{background:#122133;border:1px solid #375068;border-radius:8px;padding:11px}.metric span{color:var(--muted);display:block;font-size:11px}.metric strong{font-size:21px}
#people{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));max-width:520px;margin:13px auto;gap:3px}.person{border-radius:3px;aspect-ratio:1}
#bars{display:flex;align-items:end;gap:2px;height:145px;border-bottom:1px solid #61809b;padding-top:8px}.bar{flex:1;min-width:1px;border-radius:3px 3px 0 0}
canvas{display:block;width:100%;height:260px;background:#102132;border-radius:8px}
#time{width:min(100%,700px);accent-color:var(--accent)}
#status{color:#e7e9d3}table{border-collapse:collapse;width:100%}th,td{padding:8px 5px;border-bottom:1px solid #355068;text-align:left}
@media(max-width:850px){.grid{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}
</style></head><body><main>
<div class="eyebrow">V15 · coordinación distributiva multiagente · modelos con pesos individuales</div>
<h1>¿La aldea supera al azar para distintos k?</h1>
<p>Selecciona el número de profesiones disponibles M, el número solicitado k y la red neuronal. Se muestran recorridos VERDADEROS de los checkpoints entrenados, con decisiones simultáneas y la misma recompensa individual que en el experimento. Todos los ejemplos tienen 120 habitantes.</p>
<div class="card"><div class="controls">
<div class="field"><label>Arquitectura</label><select id="model"></select></div>
<div class="field"><label>Prof. disponibles (M)</label><select id="M"></select></div>
<div class="field"><label>Prof. solicitadas (k)</label><select id="K"></select></div>
<div class="field"><label>Reproducción</label><button id="back">Anterior</button><button id="forward">Siguiente</button><button id="play">Iniciar</button></div>
</div><p id="description"></p><input id="time" type="range" min="0" max="85" value="0"/><small id="turn"></small></div>
<div class="metrics">
<div class="metric"><span>Ración individual media</span><strong id="food">–</strong></div>
<div class="metric"><span>Media esperada del azar</span><strong id="random">–</strong></div>
<div class="metric"><span>Profesiones ocupadas</span><strong id="active">–</strong></div>
<div class="metric"><span>Reparto exactamente correcto</span><strong id="exact">–</strong></div></div>
<div class="grid">
<div class="card"><h2>Profesiones elegidas por cada agente</h2><div id="people"></div><p>Los cuadros están ordenados por identificador de agente. Los colores indican profesión. Esto NO es un mapa espacial ni mide MHU.</p></div>
<div class="card"><h2>Concentración real de profesiones</h2><div id="bars"></div><p id="distribution"></p><p>La cuota objetivo es N/k. La solución exacta exige ocupar k profesiones y distribuirlas sin diferencias de tamaño superiores a una persona; aquí todos los k elegidos dividen 120.</p></div></div>
<div class="card"><h2>Evolución a lo largo del episodio</h2><canvas id="history"></canvas><p>Verde: alimentación media. Azul: distancia al reparto funcional k. La línea horizontal amarilla marca la alimentación media esperada de una asignación completamente aleatoria.</p></div>
<div class="card"><h2>Interpretación del experimento</h2>
<p>Los modelos eligen neuronalmente entre nueve operaciones locales; sus pesos nunca se comparten entre habitantes. El agente puede mantener su profesión, imitar opciones de su vecindario, explorar o recuperar experiencias personales. El encargo k sí está disponible, pero no un censo global de profesiones.</p>
<p>El protocolo presentado usa muestreo cuando k/M es inferior a 0,5 y decisiones de máxima probabilidad cuando es igual o mayor. Cuando k/M es al menos 0,7, se añade un veto individual: si el agente ya obtiene 0,75 raciones, no abandona su profesión. Esta regla es explícita y no se ha aprendido end-to-end.</p>
<p>Un único ejemplo visual puede ir mejor o peor que la expectativa aleatoria. Las conclusiones estadísticas proceden de evaluaciones independientes de 256 sociedades por configuración, conservadas en los archivos JSON del proyecto. Superar el azar NO implica formar exactamente k grupos ni demostrar cooperación fuerte.</p></div>
</main><script>
const DATA=__DATA__, $=id=>document.getElementById(id),color=i=>'hsl('+((i*137.507+19)%360)+' 70% 60%)';
let index=0,M='80',K='30',t=0,timer=null;
function current(){return DATA.models[index].scenarios[M+'_'+K]}
function refreshOptions(){
const all=Object.values(DATA.models[index].scenarios);
const ms=[...new Set(all.map(x=>x.m))].sort((a,b)=>a-b);
$('M').innerHTML=ms.map(m=>'<option>'+m+'</option>').join('');
if(!ms.includes(+M))M=String(ms[ms.length-1]);$('M').value=M;
const ks=all.filter(x=>x.m==+M).map(x=>x.k).sort((a,b)=>a-b);
$('K').innerHTML=ks.map(k=>'<option>'+k+'</option>').join('');
if(!ks.includes(+K))K=String(ks[Math.floor(ks.length/2)]);$('K').value=K
}
function stop(){if(timer){clearInterval(timer);timer=null;$('play').textContent='Iniciar'}}
function draw(){
const caseData=current();if(!caseData)return;
t=Math.min(Math.max(t,0),caseData.frames.length-1);
let f=caseData.frames[t],max=Math.max(...f.counts,1);
$('time').max=caseData.frames.length-1;$('time').value=t;
$('turn').textContent='Turno '+t+' de '+(caseData.frames.length-1);
$('description').textContent='Cuota '+DATA.n+'/'+K+' = '+caseData.q.toFixed(2)
+' trabajadores por profesión · '+(caseData.k_trained?'Valor k visto en algún entrenamiento':'Valor k no incluido en entrenamiento')+
' · '+(K/M>=.7?'control de movilidad activo':'sin veto de movilidad');
$('food').textContent=f.food.toFixed(3);
$('random').textContent=caseData.random.toFixed(3);
$('active').textContent=f.occupied+' / '+K;
$('exact').textContent=f.exact?'SÍ':'NO';
$('people').innerHTML=f.jobs.map((x,i)=>'<div class="person" title="Agente '+i+', profesión '+x+'" style="background:'+color(x)+'"></div>').join('');
const occupations=f.counts.map((v,j)=>({v,j})).filter(x=>x.v).sort((a,b)=>b.v-a.v);
$('bars').innerHTML=occupations.map(x=>'<div class="bar" title="Prof. '+x.j+', población '+x.v+'" style="background:'+color(x.j)+';height:'+Math.max(1,x.v/max*100)+'%"></div>').join('');
$('distribution').textContent=occupations.slice(0,17).map(x=>'P'+x.j+': '+x.v).join(' · ')+(occupations.length>17?' · …':'');
plot(caseData.frames,caseData.random)
}
function plot(frames,random){
const cv=$('history'),c=cv.getContext('2d'),w=cv.clientWidth||900,h=260,ratio=window.devicePixelRatio||1;
cv.width=w*ratio;cv.height=h*ratio;c.setTransform(ratio,0,0,ratio,0,0);c.clearRect(0,0,w,h);
let x=i=>38+i/(frames.length-1)*(w-52),y=v=>12+(1-v)*(h-41);
c.font='11px system-ui';c.fillStyle='#b7d0e4';c.strokeStyle='#456176';
for(let i=0;i<=5;i++){let p=i/5,yy=y(p);c.beginPath();c.moveTo(38,yy);c.lineTo(w-10,yy);c.stroke();c.fillText(p.toFixed(1),5,yy+4)}
for(const [f,color] of [[o=>o.food,'#79d9b5'],[o=>o.d,'#7dacfa']]){
c.strokeStyle=color;c.lineWidth=2.4;c.beginPath();
frames.forEach((p,i)=>i===0?c.moveTo(x(i),y(f(p))):c.lineTo(x(i),y(f(p))));c.stroke()}
c.strokeStyle='#f9dd93';c.lineWidth=1.2;c.setLineDash([5,4]);
c.beginPath();c.moveTo(38,y(random));c.lineTo(w-10,y(random));c.stroke();c.setLineDash([]);
c.strokeStyle='rgba(255,255,255,.55)';c.beginPath();c.moveTo(x(t),10);c.lineTo(x(t),h-29);c.stroke()
}
function refresh(){refreshOptions();draw()}
$('model').innerHTML=DATA.models.map((x,i)=>'<option value="'+i+'">'+(x.recurrent?'RNN, '+x.updates+' updates':'MLP, '+x.updates+' updates')+'</option>').join('');
$('model').onchange=()=>{index=+$('model').value;t=0;stop();refresh()};
$('M').onchange=()=>{M=$('M').value;K='';t=0;stop();refresh()};
$('K').onchange=()=>{K=$('K').value;t=0;stop();draw()};
$('time').oninput=()=>{t=+$('time').value;stop();draw()};
$('back').onclick=()=>{t--;draw()};$('forward').onclick=()=>{t++;draw()};
$('play').onclick=()=>{if(timer){stop();return}timer=setInterval(()=>{if(t>=current().frames.length-1){stop();return}t++;draw()},125);$('play').textContent='Pausar'};
window.onresize=draw;
refresh();
</script></body></html>'''
(HERE/'PANEL_V15_K.html').write_text(html.replace('__DATA__',data),encoding='utf8')
print('V15_PANEL_BUILT',len(bundle),'architectures',len(CASES),'K/M combinations','bytes',len(data),flush=True)
