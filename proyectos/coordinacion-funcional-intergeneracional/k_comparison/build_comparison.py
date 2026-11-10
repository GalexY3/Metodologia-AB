"""Offline k=2 versus k=4 experiment viewer (actual saved histories)."""
from pathlib import Path
import json,html
P=Path(__file__).resolve().parent
old=P.parent/"v9_village"/"runs"/"pilot_324_d5_c0_seed1411"/"history.jsonl"
def history(p):
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
data={}
for k in (2,4):
    initial=(P/"runs"/"k2_n324_d5_seed1411"/"history.jsonl") if k==2 else old
    continuation=P/"runs"/f"k{k}_n324_continue240_seed1411"/"history.jsonl"
    records=history(initial)+history(continuation)
    data[str(k)]=[dict(updates=x["update"],food=x["stochastic"]["food_mean"],
         distance=x["stochastic"]["Dk" if k==2 or x["update"]>120 else "D4"],
         occupations=x["stochastic"]["occupied"],hunger=x["stochastic"]["hunger_fraction"],
         greedy_food=x["greedy"]["food_mean"],
         exact=x["stochastic"]["exact"]) for x in records]
audit=json.loads((P/"AUDIT_TRAPS.json").read_text(encoding="utf-8"))
pay=json.dumps(dict(data=data,audit=audit),ensure_ascii=False).replace("</","<\\/")
template=r'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>¿Dos profesiones o cuatro? · Aldea MARL</title>
<style>
:root{color-scheme:dark;--bg:#101825;--card:#1b2a3c;--fg:#e9f3ff;--muted:#a8bac8;--rule:#34495b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:1170px;margin:auto;padding:27px 20px 65px}
h1{font-size:clamp(28px,3vw,40px);margin:3px 0 8px;letter-spacing:-.03em}
h2{font-size:20px;margin:0 0 12px}p{color:var(--muted);margin:5px 0 14px}
label{color:var(--muted);margin-right:6px}select{border:1px solid #526880;background:#293f55;color:var(--fg);padding:9px;border-radius:7px}
.card{border:1px solid var(--rule);background:var(--card);padding:20px;border-radius:15px;margin-top:16px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
canvas{display:block;width:100%;height:245px}
.kicker{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#79dbcc}
.legend{display:flex;gap:17px;flex-wrap:wrap;margin-top:8px;font-size:13px;color:var(--muted)}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:6px}
.bars{display:flex;align-items:flex-end;gap:3px;border-bottom:1px solid #637485;height:155px;margin-top:13px}
.bar{flex:1;min-width:0;border-radius:3px 3px 0 0}
@media(max-width:780px){.two{grid-template-columns:1fr}main{padding:15px 12px}}
</style></head><body><main>
<div class="kicker">Simulación de aprendizaje individual · 10 profesiones</div>
<h1>¿Dos grupos o cuatro?</h1>
<p>La recompensa es individual; los agentes desconocen el objetivo de ocupación, la cuota, el censo global y las recompensas alternativas. N=324, cinco vecinos, la misma arquitectura y el mismo presupuesto de 240 actualizaciones.</p>
<div class="card"><label for="metric">Variable</label><select id="metric">
<option value="food">Alimentación media, máximo 1</option><option value="distance">Distancia a la distribución óptima, mínimo 0</option>
<option value="occupations">Profesiones ocupadas</option><option value="hunger">Fracción con hambre</option></select>
<canvas id="chart"></canvas><div class="legend"><span><i class="dot" style="background:#83baf4"></i>Dos profesiones ideales (q=162)</span><span><i class="dot" style="background:#f3b176"></i>Cuatro profesiones ideales (q=81)</span></div>
<p style="font-size:12px">Evaluación estocástica. Una semilla de entrenamiento y 24 sociedades por evaluación; esta gráfica es exploratoria. La línea en 0,5 marca el posible bloqueo subóptimo en alimentación.</p></div>
<div class="two">
<div class="card"><h2>k=2, política determinista final</h2><p>Ocupaciones en una sociedad nueva, después de 40 turnos.</p><div id="bars2" class="bars"></div><p id="label2"></p></div>
<div class="card"><h2>k=4, política determinista final</h2><p>Ocupaciones en una sociedad nueva, después de 40 turnos.</p><div id="bars4" class="bars"></div><p id="label4"></p></div>
</div>
<div class="card"><h2>Lectura científica</h2>
<p>Con k=2 el modelo colapsa en una profesión de 324 trabajadores y obtiene 0,5 raciones por persona. Con k=4 suele ocupar dos profesiones sobredimensionadas, también con 0,5 raciones medias. Ninguna de las condiciones llega a la solución deseada en la batería de 324 individuos.</p>
<p>La conducta estocástica deja ocupaciones residuales en otras profesiones. Que una política determinista colapse no demuestra cooperación ni aprendizaje del reparto ideal. Para extraer conclusiones causales sobre k hacen falta otras semillas y condiciones informativas.</p></div>
</main><script>
const O=__DATA__;
const C=document.getElementById("chart");
const pal=["#83baf4","#f3b176"];
const colors=["#8bbbf0","#f4ba83","#8bd2aa","#d2a8e4","#ef9eaa","#e5ce80","#8cced6","#a4a0e3","#c5bd82","#d1a892"];
const fmt=x=>Number(x).toFixed(3);
function plot(){
let k=document.getElementById("metric").value,ctx=C.getContext("2d"),w=C.clientWidth||800,h=245,ratio=window.devicePixelRatio||1;
C.width=w*ratio;C.height=h*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,w,h);
const values=Object.values(O.data).flatMap(x=>x.map(p=>p[k])),max=k==="occupations"?10:1;
const left=44,top=12,right=20,bottom=28;
const X=x=>left+(x/240)*(w-left-right),Y=y=>top+(max-y)/max*(h-top-bottom);
ctx.font="11px system-ui";ctx.strokeStyle="#3e5267";ctx.fillStyle="#bdd0e1";
for(let i=0;i<=5;i++){const y=max*i/5,p=Y(y);ctx.beginPath();ctx.moveTo(left,p);ctx.lineTo(w-right,p);ctx.stroke();ctx.fillText(y.toFixed(k==="occupations"?0:1),4,p+4)}
for(const [i,kval] of ["2","4"].entries()){const arr=O.data[kval];ctx.strokeStyle=pal[i];ctx.lineWidth=3;
ctx.beginPath();arr.forEach((p,j)=>j?ctx.lineTo(X(p.updates),Y(p[k])):ctx.moveTo(X(p.updates),Y(p[k])));ctx.stroke();
arr.forEach(p=>{ctx.fillStyle=pal[i];ctx.beginPath();ctx.arc(X(p.updates),Y(p[k]),2.2,0,6.283);ctx.fill()})}
}
function bars(){
for(const k of [2,4]){
 const a=O.audit.find(x=>x.k===k&&x.mode==="greedy"),v=a.first_world_counts,max=Math.max(...v);
 const box=document.getElementById("bars"+k);
 box.innerHTML=v.map((n,i)=>"<div class='bar' title='Profesión "+i+": "+n+"' style='height:"+Math.max(1,n/max*100)+"%;background:"+colors[i]+"'></div>").join("");
 document.getElementById("label"+k).textContent="Trabajadores: "+v.join(" · ")+" · raciones medias "+fmt(a.food);
}
}
document.getElementById("metric").onchange=plot;window.addEventListener("resize",plot);
plot();bars();
</script></body></html>'''
html=template.replace("__DATA__",pay)
(P/"COMPARACION_K2_K4.html").write_text(html,encoding="utf-8")
print("HTML",P/"COMPARACION_K2_K4.html",len(html),"bytes",len(data["2"]),len(data["4"]))
