"""Create fully self-contained HTML dashboard from real village histories and replays."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
runs={}
for folder in sorted((ROOT/"runs").glob("pilot_*")):
    history=folder/"history.jsonl"
    if not history.exists():continue
    rows=[json.loads(s) for s in history.read_text(encoding="utf-8").splitlines() if s.strip()]
    if not rows:continue
    config=json.loads((folder/"config.json").read_text(encoding="utf-8"))
    replay=json.loads((folder/"replay.json").read_text(encoding="utf-8")) if (folder/"replay.json").exists() else None
    status=json.loads((folder/"status.json").read_text(encoding="utf-8")) if (folder/"status.json").exists() else {}
    runs[folder.name]=dict(history=rows,config=config,status=status,replay=replay)
baseline=json.loads((ROOT/"BASELINES.json").read_text(encoding="utf-8")) if (ROOT/"BASELINES.json").exists() else {}
payload=json.dumps({"arms":runs,"baselines":baseline},ensure_ascii=False).replace("</","<\\/")
template=r'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>La aldea · Entrenamiento individual MARL</title>
<style>
:root{color-scheme:dark;--bg:#0b1422;--card:#172637;--fg:#ecf5ff;--muted:#a9bdce;--border:#33485c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1400px;padding:25px 20px 65px;margin:auto}
h1{font-size:36px;margin:0 0 8px;letter-spacing:-.03em}
h2{font-size:20px;margin:0 0 10px}p{color:var(--muted);margin:5px 0 12px}
.kicker{color:#79d8c5;font-size:12px;letter-spacing:.15em;text-transform:uppercase;font-weight:700}
.panel{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px;min-width:0;margin-top:16px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
select,button{background:#263d53;color:var(--fg);border:1px solid #4b6275;border-radius:8px;padding:8px 12px;cursor:pointer}
input[type=range]{width:100%;accent-color:#6dd4c4}.controls{display:flex;flex-wrap:wrap;gap:9px;align-items:center}
canvas{width:100%;height:275px;display:block}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;white-space:nowrap;font-size:13px}
th,td{padding:9px 8px;text-align:left;border-bottom:1px solid #3a5061}
th{color:#aec2d1}td.num{text-align:right;font-variant-numeric:tabular-nums}
#cells{display:grid;gap:2px;width:min(100%,520px);margin:12px auto 0}
.node{aspect-ratio:1;border-radius:2px}
#bars{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:6px;align-items:end;height:145px;padding-top:8px}
.bgroup{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:135px}
.bar{width:100%;min-height:1px;border-radius:2px 2px 0 0}
.caption{font-size:12px;color:var(--muted)}.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;margin-top:10px}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}
@media(max-width:780px){.grid{grid-template-columns:1fr}main{padding:16px 12px}h1{font-size:27px}}
</style></head><body><main>
<div class="kicker">Experimento · Aprendizaje exclusivamente individual</div>
<h1>Aldea de diez profesiones</h1>
<p>La aldea dispone de diez profesiones equivalentes. La máxima producción por individuo se consigue con cuatro grupos de N/4 miembros. Los agentes desconocen el censo, la cuota ideal, el número de profesiones óptimo y sus recompensas contrafácticas.</p>
<div class="panel"><h2>Evolución del aprendizaje</h2><div class="controls">
<label for="metric">Variable</label><select id="metric"><option value="food_mean">Raciones medias</option><option value="D4">Distancia al óptimo</option><option value="hunger_fraction">Fracción con hambre</option><option value="occupied">Profesiones ocupadas</option><option value="churn">Cambios de profesión</option></select>
<label for="mode">Evaluación</label><select id="mode"><option value="stochastic">Estocástica</option><option value="greedy">Determinista</option></select>
</div><canvas id="chart"></canvas><div class="legend" id="legend"></div>
<p class="caption">Una curva por condición de entrenamiento; una sola semilla inicial por condición. Evaluaciones de desarrollo, no test confirmatorios.</p></div>
<div class="panel"><h2>Resultados finales por condición</h2><div class="scroll">
<table><thead><tr><th>Modelo</th><th>N</th><th>Vecinos</th><th>Mensajes</th><th>Actualizaciones</th><th>Raciones</th><th>D₄</th><th>Profesiones</th><th>Hambre</th><th>Exactas</th></tr></thead><tbody id="results"></tbody></table></div></div>
<div class="grid">
<div class="panel"><h2>Una sociedad observada</h2><div class="controls">
<label>Modelo</label><select id="arm"></select><button id="prev">Anterior</button><button id="next">Siguiente</button><button id="play">Reproducir</button>
</div><input type="range" id="frame" min="0" max="0" value="0">
<p id="frameinfo"></p><div id="cells"></div>
<p class="caption">Cada cuadrado es un habitante; su color indica la profesión. Fotogramas de una sociedad real de desarrollo con política congelada y decisión estocástica.</p></div>
<div class="panel"><h2>Ocupación de las diez profesiones</h2><div id="bars"></div>
<p id="distribution"></p><h2>Controles sin entrenamiento</h2><div class="scroll">
<table><thead><tr><th>N</th><th>Vecinos</th><th>Política</th><th>Raciones</th><th>D₄</th></tr></thead><tbody id="baseline"></tbody></table></div>
<p class="caption">El porcentaje de hambre se refiere a quienes obtienen menos de 0,85 raciones. De momento no existe mortalidad real; es un indicador.</p></div>
</div>
<p class="caption" style="margin-top:20px">Panel autónomo sin Internet ni dependencias externas. Curvas, pesos y resultados procedentes de la carpeta de investigación v9_village.</p>
</main><script>
"use strict";
const DATA=__PAYLOAD__;
const $=id=>document.getElementById(id);
const colors=["#7abce5","#e9b676","#8fcaa3","#d1a0e6","#f68e9f","#83d9d0","#b2a0f0","#e8d67d","#9caee3","#dab69f"];
const linecolors=["#72c6f0","#f7ba85","#8fd9b0","#d4a3f8","#f18b98","#c9d875","#87bcd6","#debe81"];
const arms=Object.entries(DATA.arms).sort((a,b)=>a[0].localeCompare(b[0]));
const fmt=(v,p=3)=>Number.isFinite(Number(v))?Number(v).toFixed(p):"—";
const label=n=>n.replace("pilot_","").replace(/_seed\d+/,"").replaceAll("_"," ");
let active=arms[0]?arms[0][0]:"",t=0,playing=null;
function renderRows(){
 $("results").innerHTML=arms.map(a=>{
 const name=a[0],item=a[1],row=item.history.at(-1),cfg=item.config.config,r=row.stochastic;
 return "<tr><td>"+label(name)+"</td><td>"+cfg.n+"</td><td>"+cfg.degree+"</td><td>"+(cfg.communication?"Sí":"No")+"</td><td>"+row.update+"</td><td class='num'>"+fmt(r.food_mean)+"</td><td class='num'>"+fmt(r.D4)+"</td><td class='num'>"+fmt(r.occupied,2)+"</td><td class='num'>"+fmt(100*r.hunger_fraction,1)+"%</td><td class='num'>"+r.exact+"/"+r.worlds+"</td></tr>";
 }).join("");
 $("arm").innerHTML=arms.map(a=>"<option value='"+a[0]+"'>"+label(a[0])+"</option>").join("");
 $("arm").value=active;
 let base=DATA.baselines.records||[];
 $("baseline").innerHTML=base.map(r=>"<tr><td>"+r.n+"</td><td>"+r.degree+"</td><td>"+r.arm+"</td><td class='num'>"+fmt(r.final.food_mean)+"</td><td class='num'>"+fmt(r.final.D4)+"</td></tr>").join("");
}
function chart(){
 const cn=$("chart"),ctx=cn.getContext("2d"),w=cn.clientWidth||700,h=275,pixel=window.devicePixelRatio||1;
 cn.width=Math.round(w*pixel);cn.height=Math.round(h*pixel);ctx.setTransform(pixel,0,0,pixel,0,0);ctx.clearRect(0,0,w,h);
 const key=$("metric").value,mode=$("mode").value;
 const series=arms.map((a,i)=>({name:a[0],color:linecolors[i%linecolors.length],
 points:a[1].history.map(r=>({x:r.update,y:r[mode]&&r[mode][key]})).filter(v=>Number.isFinite(v.y))}));
 const all=series.flatMap(s=>s.points);
 if(!all.length){ctx.fillStyle="#acbfd0";ctx.fillText("Sin evaluaciones",40,90);return}
 const hi=key==="occupied"?10:Math.max(1,...all.map(p=>p.y)),maxX=Math.max(120,...all.map(p=>p.x));
 const left=48,right=16,top=12,bottom=27;
 const x=a=>left+a/maxX*(w-left-right);
 const y=a=>top+(hi-a)/hi*(h-top-bottom);
 ctx.strokeStyle="#375267";ctx.fillStyle="#b6c6d4";ctx.font="11px system-ui";
 for(let i=0;i<=5;i++){const py=y(i*hi/5);ctx.beginPath();ctx.moveTo(left,py);ctx.lineTo(w-right,py);ctx.stroke();ctx.fillText((i*hi/5).toFixed(key==="occupied"?0:2),3,py+4)}
 for(const s of series){if(!s.points.length)continue;ctx.beginPath();ctx.strokeStyle=s.color;ctx.lineWidth=2.1;
 s.points.forEach((p,i)=>i?ctx.lineTo(x(p.x),y(p.y)):ctx.moveTo(x(p.x),y(p.y)));ctx.stroke();}
 $("legend").innerHTML=series.map(s=>"<span><i class='dot' style='background:"+s.color+"'></i>"+label(s.name)+"</span>").join("");
}
function displayFrame(){
 const seq=DATA.arms[active]&&DATA.arms[active].replay&&DATA.arms[active].replay.frames;
 if(!seq||!seq.length){$("cells").innerHTML="";$("frameinfo").textContent="Sin datos";return}
 t=Math.max(0,Math.min(t,seq.length-1));const f=seq[t],n=f.colors.length,side=Math.round(Math.sqrt(n));
 $("frame").max=seq.length-1;$("frame").value=t;
 $("frameinfo").textContent="Turno "+f.t+"/"+(seq.length-1)+" · Raciones "+fmt(f.food)+" · D₄ "+fmt(f.D4);
 $("cells").style.gridTemplateColumns="repeat("+side+",minmax(0,1fr))";
 $("cells").innerHTML=f.colors.map((j,i)=>"<div class='node' style='background:"+colors[j]+"' title='Habitante "+(i+1)+", profesión "+j+"'></div>").join("");
 const biggest=Math.max(1,...f.counts);
 $("bars").innerHTML=f.counts.map((num,i)=>"<div class='bgroup'><div class='bar' style='height:"+Math.max(1,100*num/biggest)+"%;background:"+colors[i]+"' title='Profesión "+i+": "+num+"'></div><div class='caption'>"+i+"</div></div>").join("");
 $("distribution").textContent="Habitantes por profesión: "+f.counts.join(" · ");
}
function stop(){if(playing){clearInterval(playing);playing=null;$("play").textContent="Reproducir"}}
$("metric").onchange=chart;$("mode").onchange=chart;window.onresize=chart;
$("arm").onchange=()=>{active=$("arm").value;t=0;stop();displayFrame()};
$("frame").oninput=()=>{t=Number($("frame").value);displayFrame()};
$("prev").onclick=()=>{t--;displayFrame()};$("next").onclick=()=>{t++;displayFrame()};
$("play").onclick=()=>{if(playing){stop();return}
$("play").textContent="Pausar";
playing=setInterval(()=>{const seq=DATA.arms[active].replay.frames;
if(t>=seq.length-1){stop();return}t++;displayFrame()},270)};
renderRows();chart();displayFrame();
</script></body></html>'''
html=template.replace("__PAYLOAD__",payload)
(ROOT/"PANEL_ALDEA.html").write_text(html,encoding="utf-8")
print("DASHBOARD",len(runs),"models",len(html),"bytes")
