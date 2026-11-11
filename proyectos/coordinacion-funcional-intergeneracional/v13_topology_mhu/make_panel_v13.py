"""One-file, offline V13 topology and finite-MHU diagnostics dashboard."""
from pathlib import Path
import json,numpy as np
from network_v13 import HERE,build_graph,coordinates
from mhu_v13 import reference_balanced,partial_spectrum
from network_v13 import base

models=[]
for folder in sorted((HERE/'runs').glob('v13_N*')):
    file=HERE/'evaluations'/(folder.name+'_EVAL.json')
    if not file.exists():continue
    x=json.loads(file.read_text('utf8'))
    history=[json.loads(s) for s in (folder/'history.jsonl').read_text('utf8').splitlines() if s.strip()]
    info=x['network'];n=info['n'];top=info['network'];deg=info['requested_mean_degree'];seed=info['graph_seed']
    coords=coordinates(n,top,seed)
    adjacency=build_graph(n,deg,top,seed)
    edges=[[int(i),int(j)] for i,row in enumerate(adjacency) for j in row if j>=0 and j>i]
    samples={}
    for e in x['experiments']:
        if e['graph_seed']!=seed:continue
        if e['baseline']!='learned' or e['init']!='random':continue
        if e['task'] not in ('known_k2_m10','known_k4_m20','unseen_k5_m30'):continue
        example=e['by_seed'][0]
        steps=example['replay']
        if not steps:continue
        final=example['checks'][str(steps[-1]['t'])]
        mean_window=[]
        for s in e['by_seed']:
            d=s['checks'][str(steps[-1]['t'])]['finite_window_ratio']
            if d is not None:mean_window.append(d)
        samples[e['task']]=dict(task=e['task'],m=e['m'],k=e['k'],
            food=e['food'],dist=e['d'],exact=e['exact'],
            spectral=e['low_spectral_ratio'],
            window=float(np.mean(mean_window)) if mean_window else None,
            coverage=final['alive_spectrum']['mean_resolved_components'],
            samples=steps)
    if 'known_k4_m20' in samples:
        m=20;k=4
        marked=reference_balanced(n,m,k,coords,seed=10001,kind='low_spectral',swaps=2600)
        samples['known_k4_m20']['constructed_mhu_reference']={
          'jobs':[int(v) for v in marked],
          'spectral':partial_spectrum(marked,coords)['mean_ratio']}
    models.append(dict(id=folder.name,n=n,network=info,positions=coords.tolist(),
        edges=edges,samples=samples,
        history=[dict(update=q['update'],known=q['evaluations'].get('train_k2_m10',{}).get('food'),
              new=q['evaluations'].get('new_k5_m30',{}).get('food')) for q in history]))
data=json.dumps(dict(models=models,
        note='All diagrams are real model snapshots except the explicitly labeled constructed MHU reference. Finite low-q ratio is NOT strict MHU.'),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
html=r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>V13 · Red social y patrón espacial de las profesiones</title>
<style>
:root{color-scheme:dark;--bg:#0e1722;--card:#1a2a3c;--fg:#e7f3ff;--muted:#aabccf;--stroke:#3b5167;--acc:#79d0c2}
*{box-sizing:border-box}body{font:14px/1.52 system-ui,Segoe UI,Arial;background:var(--bg);color:var(--fg);margin:0}
main{max-width:1490px;margin:auto;padding:24px 18px 72px}h1{font-size:32px;font-weight:680;margin:3px 0}
h2{font-size:19px;margin:0 0 8px}h3{font-size:15px}p{color:var(--muted);margin:5px 0 13px}
.eyebrow{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--acc)}
.grid{display:grid;grid-template-columns:minmax(400px,1.2fr) minmax(310px,.8fr);gap:15px}
.card{background:var(--card);border:1px solid var(--stroke);padding:18px;border-radius:14px;margin-bottom:15px}
select,button{background:#2d4258;border:1px solid #5a778d;color:var(--fg);padding:9px;border-radius:7px;cursor:pointer}
label{color:var(--muted);font-size:12px}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:end;margin-bottom:12px}
.input{display:flex;flex-direction:column;gap:5px}button:hover{background:#43627c}
canvas{display:block;width:100%;height:350px;background:#142334;border-radius:9px}
#curve{height:240px}#graph{height:480px}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.metric{background:#142333;border:1px solid #304558;border-radius:8px;padding:11px}
.metric small{display:block;color:var(--muted);font-size:11px}.metric strong{font-size:20px;font-weight:700}
#occupations{display:flex;align-items:end;gap:2px;height:130px;padding-top:10px;border-bottom:1px solid #536a80}
.bar{flex:1;min-width:2px;border-radius:3px 3px 0 0}
table{border-collapse:collapse;width:100%;font-size:12px}th,td{padding:8px 7px;border-bottom:1px solid #33495d;text-align:left}
th{color:#b2cce0}td.num{text-align:right;font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}.legend{display:flex;gap:17px;flex-wrap:wrap;color:var(--muted);font-size:12px;margin:10px 0}
.chip{display:inline-block;width:12px;height:7px;border-radius:2px;margin-right:5px}
#time{width:min(100%,450px)}.subtitle{color:var(--fg);margin-top:8px}
@media(max-width:880px){.grid{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}#graph{height:350px}}
</style></head><body><main>
<div class="eyebrow">Laboratorio de coordinación · variable M/k · topologías y física estadística</div>
<h1>¿Qué estructura social produce qué organización espacial?</h1>
<p>Experimentación con redes de distinta proximidad, número de enlaces y heterogeneidad. Se distingue la economía global (alimentación y tamaño de profesiones) de la multihiperuniformidad (fluctuaciones espaciales de <strong>cada</strong> profesión). Los modelos usan pesos individuales separados.</p>
<div class="card"><div class="controls">
<div class="input" style="flex:2;min-width:260px"><label>Seleccionar sociedad entrenada</label><select id="model"></select></div>
<div class="input" style="flex:1;min-width:170px"><label>Objetivo económico</label><select id="scenario">
<option value="known_k2_m10">M=10 / k=2, entrenado</option>
<option value="known_k4_m20">M=20 / k=4, entrenado</option>
<option value="unseen_k5_m30">M=30 / k=5, nuevo</option>
</select></div>
<div class="input"><label>Tipo de patrón</label><select id="pattern"><option value="learned">Agentes entrenados</option><option value="constructed">MHU construido (control)</option></select></div>
</div><div id="networkMeta" class="subtitle"></div></div>
<div class="grid">
<div><div class="card"><h2>Red real de contactos y profesión de cada habitante</h2><canvas id="graph"></canvas>
<div class="controls" style="margin-top:12px"><button id="back">Anterior</button><button id="next">Siguiente</button><button id="play">Reproducir</button><label>Mostrar enlaces</label><input id="showlinks" type="checkbox" checked><label>Opacidad</label><input id="linkalpha" type="range" min="0" max="30" value="10"></div>
<label id="tlabel">Turno 0</label><input id="time" type="range" min="0" max="4" value="0">
<p>La posición es espacial y permanece fija. Las líneas son enlaces sociales reales. Los colores son profesiones; distintos números de personas del mismo color pueden agruparse geográficamente.</p></div>
<div class="card"><h2>Aprendizaje en la misma red</h2><canvas id="curve"></canvas>
<div class="legend"><span><i class="chip" style="background:#7ed6b2"></i>M=10/k=2, entrenado</span><span><i class="chip" style="background:#7baef4"></i>M=30/k=5, nuevo</span></div></div></div>
<div><div class="card"><h2>Economía frente a orden espacial</h2><div class="metrics">
<div class="metric"><small>Alimento medio</small><strong id="food">–</strong></div>
<div class="metric"><small>Distancia Dk</small><strong id="dk">–</strong></div>
<div class="metric"><small>Ratio S bajo-q / azar</small><strong id="spectral">–</strong></div>
<div class="metric"><small>Varianza ventanas / azar</small><strong id="window">–</strong></div>
</div><p id="interpretation"></p><h3>Distribución de profesiones</h3><div id="occupations"></div><p id="occupText"></p>
<p>Un ratio <b>1</b> es el promedio de etiquetas aleatorias con las mismas ocupaciones y posiciones. Un ratio <b>menor que 1</b> indica supresión de fluctuaciones; superior a 1 indica tendencia a agregación espacial. Una muestra finita jamás demuestra el límite MHU estricto.</p></div>
<div class="card"><h2>Comparación entre redes al final de la evaluación</h2><div class="scroll"><table><thead><tr><th>Grafo</th><th>N</th><th>Links</th><th>Comida k5</th><th>Ratio S</th></tr></thead><tbody id="comparison"></tbody></table></div><p>Una sola semilla de entrenamiento por grafo en la primera batería. Las filas son comparaciones exploratorias, no rangos estadísticos confirmados.</p></div></div>
</div>
</main><script>
const DATA=__DATA__;
const $=id=>document.getElementById(id);
const hue=i=>'hsl('+((i*137.508+16)%360)+' 72% 61%)';
let selected=DATA.models.find(m=>m.id.includes('N120_torus_d4'))||DATA.models[0],frame=0,timer=null;
function num(x,d=3){return x==null?'—':Number(x).toFixed(d)}
function init(){let ms=[...DATA.models].sort((a,b)=>a.n-b.n||a.id.localeCompare(b.id));$('model').innerHTML=ms.map(m=>'<option value="'+m.id+'">'+m.id+'</option>').join('');$('model').value=selected.id;refresh()}
function scenario(){let s=selected.samples[$('scenario').value];if(!s){let k=Object.keys(selected.samples)[0];$('scenario').value=k;s=selected.samples[k]}return s}
function latest(){let s=scenario();if(!s)return null;const positive=$('pattern').value==='constructed';
if(positive&&s.constructed_mhu_reference){let r=s.constructed_mhu_reference;return {jobs:r.jobs,t:0,food:1,mhu:{mean_ratio:r.spectral}}}
if(!s.samples?.length)return null;frame=Math.min(frame,s.samples.length-1);return s.samples[frame]}
function clearTimer(){if(timer){clearInterval(timer);timer=null;$('play').textContent='Reproducir'}}
function drawGraph(){let d=latest();const c=$('graph'),ctx=c.getContext('2d'),W=c.clientWidth,H=c.clientHeight,ratio=window.devicePixelRatio||1;
c.width=W*ratio;c.height=H*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,W,H);
if(!d)return;
const pts=selected.positions, sx=x=>19+x*(W-38),sy=y=>19+y*(H-38);
if($('showlinks').checked){let alpha=+$('linkalpha').value/100;ctx.strokeStyle='rgba(171,207,226,'+alpha+')';ctx.lineWidth=.8;
for(let [i,j] of selected.edges){let a=pts[i],b=pts[j],dx=b[0]-a[0],dy=b[1]-a[1];dx-=Math.round(dx);dy-=Math.round(dy);
for(let ox=-1;ox<=1;ox++)for(let oy=-1;oy<=1;oy++){let x0=a[0]+ox,y0=a[1]+oy,x1=x0+dx,y1=y0+dy;
if((x0<0&&x1<0)||(x0>1&&x1>1)||(y0<0&&y1<0)||(y0>1&&y1>1))continue;
ctx.beginPath();ctx.moveTo(sx(x0),sy(y0));ctx.lineTo(sx(x1),sy(y1));ctx.stroke()}}}
for(let i=0;i<pts.length;i++){let p=pts[i],role=d.jobs[i];ctx.fillStyle=hue(role);ctx.strokeStyle='#101922';ctx.lineWidth=.8;
ctx.beginPath();ctx.arc(sx(p[0]),sy(p[1]),selected.n>80?4:5.4,0,Math.PI*2);ctx.fill();ctx.stroke()}
$('tlabel').textContent='Turno '+d.t+' · '+d.jobs.length+' agentes';
let marks={};for(let k of d.jobs)marks[k]=(marks[k]||0)+1;
let h=Math.max(...Object.values(marks));let s=scenario();let nprof=s.m;
$('occupations').innerHTML=Array.from({length:nprof},(_,i)=>'<div class="bar" style="background:'+hue(i)+';height:'+Math.max(1,((marks[i]||0)/h*100))+'%" title="Profesión '+i+': '+(marks[i]||0)+'"></div>').join('');
$('occupText').textContent=Object.entries(marks).map(([i,n])=>i+': '+n).join(' · ');
$('food').textContent=num(d.food);
$('spectral').textContent=num(d.mhu?.mean_ratio);
$('window').textContent=$('pattern').value==='constructed'?'Control':(d.t===s.samples.at(-1).t?num(s.window):'—');
let q=d.jobs.length/s.k;
let exactDist=1-Object.values(marks).sort((a,b)=>b-a).slice(0,s.k).reduce((total,c)=>total+Math.min(c,q),0)/d.jobs.length;
$('dk').textContent=num(exactDist);
let r=d.mhu?.mean_ratio;
$('interpretation').textContent=$('pattern').value==='constructed'
?'Control construido: ocupaciones iguales y posiciones seleccionadas específicamente para reducir amplitudes de baja frecuencia. No es aprendizaje.'
:r==null?'No hay suficientes profesiones ocupadas para medir este indicador con rigor.'
:r>1.1?'En este fotograma hay más fluctuación territorial por profesión que bajo etiquetas barajadas. No es MHU.':
r<.8?'Se observan fluctuaciones de baja frecuencia menores que el control aleatorio en este fotograma. Es una señal FINITA, no MHU estricta.':
'El resultado está próximo a la referencia de etiquetas aleatorias.';
}
function plot(){let canvas=$('curve'),ctx=canvas.getContext('2d'),W=canvas.clientWidth,H=canvas.clientHeight,k=window.devicePixelRatio||1;
canvas.width=W*k;canvas.height=H*k;ctx.setTransform(k,0,0,k,0,0);ctx.clearRect(0,0,W,H);
const rows=selected.history,max=Math.max(1,...rows.map(q=>q.update));
const x=t=>36+(t/max)*(W-50),y=v=>12+(1-v)*(H-40);
ctx.font='12px system-ui';ctx.strokeStyle='#46596d';ctx.fillStyle='#bccada';
for(let i=0;i<=5;i++){let v=i/5,yy=y(v);ctx.beginPath();ctx.moveTo(36,yy);ctx.lineTo(W-10,yy);ctx.stroke();ctx.fillText(v.toFixed(1),3,yy+4)}
for(let [key,col] of [['known','#7ed6b2'],['new','#7baef4']]){ctx.strokeStyle=col;ctx.lineWidth=2.4;ctx.beginPath();
rows.forEach((r,i)=>{if(r[key]==null)return;if(i===0)ctx.moveTo(x(r.update),y(r[key]));else ctx.lineTo(x(r.update),y(r[key]))});ctx.stroke()}}
function compare(){let ms=DATA.models.filter(m=>m.samples.unseen_k5_m30).sort((a,b)=>a.n-b.n||a.network.network.localeCompare(b.network.network));
$('comparison').innerHTML=ms.map(m=>{let s=m.samples.unseen_k5_m30;return '<tr><td>'+m.network.network+' (d'+m.network.requested_mean_degree+')</td><td class="num">'+m.n+'</td><td class="num">'+m.network.links+'</td><td class="num">'+num(s.food)+'</td><td class="num">'+num(s.spectral)+'</td></tr>'}).join('')}
function refresh(){let n=selected.network;$('networkMeta').textContent='Red '+n.network+' · N='+n.n+' · grado medio '+num(n.mean_degree,2)+' (mín '+n.min_degree+', máx '+n.max_degree+') · '+n.links+' enlaces · clustering '+num(n.clustering)+' · distancia social '+num(n.path_length);
let s=scenario();$('time').max=Math.max(0,(s?.samples?.length||1)-1);$('time').value=frame;
$('pattern').querySelector('option[value=constructed]').disabled=!s?.constructed_mhu_reference;
if($('pattern').value==='constructed'&&!s?.constructed_mhu_reference)$('pattern').value='learned';
drawGraph();plot();compare()}
$('model').onchange=()=>{selected=DATA.models.find(m=>m.id===$('model').value);frame=0;clearTimer();refresh()};
$('scenario').onchange=()=>{frame=0;clearTimer();refresh()};
$('pattern').onchange=()=>{clearTimer();drawGraph()};
$('showlinks').onchange=drawGraph;$('linkalpha').oninput=drawGraph;
$('time').oninput=()=>{frame=+$('time').value;clearTimer();drawGraph()};
$('back').onclick=()=>{frame=Math.max(0,frame-1);$('time').value=frame;drawGraph()};
$('next').onclick=()=>{frame=Math.min(scenario().samples.length-1,frame+1);$('time').value=frame;drawGraph()};
$('play').onclick=()=>{if(timer){clearTimer();return}if($('pattern').value==='constructed')$('pattern').value='learned';
timer=setInterval(()=>{let l=scenario().samples.length;if(frame>=l-1){clearTimer();return}frame++;$('time').value=frame;drawGraph()},500);$('play').textContent='Pausar'};
window.onresize=()=>{drawGraph();plot()};init();
</script></body></html>'''
(HERE/'V13_PANEL_INTERACTIVO.html').write_text(html.replace('__DATA__',data),encoding='utf8')
print('DASHBOARD_BUILT',len(models),'trained models',len(data),'JSON chars',flush=True)
